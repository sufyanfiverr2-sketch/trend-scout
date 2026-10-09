"""Core logic for TrendScout.

Two modes:
1. Free Tier Mode (default): pulls live signals via `fetchers.py` (Google Trends PK,
   Reddit memes, Instagram trends) and feeds them to Gemini.
   Consumes ZERO paid quota and stays 100% on the free tier.
2. Search Grounding Mode (optional): uses Gemini's built-in Google Search tool for
   users with paid search quota enabled.
"""

from __future__ import annotations

import copy
import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Any, List, Literal, Optional, Type, TypeVar
from urllib.parse import quote_plus

from google import genai
from pydantic import BaseModel, Field

import fetchers

MODEL = "gemini-3.5-flash"
FALLBACK_MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]

T = TypeVar("T", bound=BaseModel)


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #
class Trend(BaseModel):
    name: str = Field(description="Short, catchy name of the trend.")
    category: Literal[
        "Funny / Meme", "Campus Life / Relatable", "Audio / Sound", "Format / POV", "Challenge", "Editing Style"
    ]
    region: Literal["Global", "Local"] = Field(
        description="'Local' if the trend is specific to the society's country/region (e.g. Pakistan/Desi)."
    )
    status: Literal["Rising", "Peak", "Fading"] = Field(
        description="Where the trend is in its lifecycle. Prefer Rising/Peak trends."
    )
    description: str = Field(description="Clear explanation of what the trend looks and sounds like.")
    why_funny: str = Field(description="Why this makes people laugh; what's the punchline or irony.")
    how_to_adapt: str = Field(
        description="A hilarious, non-technical campus skit or meme adaptation for university students."
    )
    example_hook: str = Field(description="Opening text overlay or dialogue for the first 3 seconds.")
    reference_video_search_query: str = Field(
        description="Exact search query to see the best viral video of this trend on Instagram or YouTube (e.g. 'instagram reels trend bro really thought audio')."
    )
    reference_video_url: str = Field(
        default="",
        description="Direct link or search link to watch the best example video.",
    )
    effort: Literal["Low", "Medium", "High"] = Field(description="Filming effort required.")


class TrendReport(BaseModel):
    overview: str = Field(description="2-3 sentence summary of what's going viral and making students laugh right now.")
    trends: List[Trend]


class Shot(BaseModel):
    seconds: str = Field(description="Time range, e.g. '0-3s'.")
    visual: str = Field(description="What the camera shows / actor's facial expression / physical action.")
    text_overlay: str = Field(description="On-screen text (empty string if none).")
    voiceover: str = Field(description="Spoken dialogue or audio punchline (empty string if none).")


class ReelIdea(BaseModel):
    title: str
    trend_used: str = Field(description="Which funny trend/meme/audio this rides on.")
    hook: str = Field(description="The hilarious scroll-stopping hook in the first 1-3 seconds.")
    concept: str = Field(description="The joke, irony, or funny premise behind this reel.")
    shot_list: List[Shot]
    audio_suggestion: str = Field(description="Specific viral audio, meme sound effect, or dialogue.")
    caption: str = Field(description="Engaging, humorous Instagram caption with relatable emojis and call-to-action.")
    hashtags: List[str] = Field(description="10-15 viral and relatable hashtags.")
    best_posting_time: str = Field(description="Best time to post in local timezone.")
    props_needed: List[str]
    duration_seconds: int
    virality_score: int = Field(description="Rating from 1-10 on comedy & shareability.")
    why_it_works: str = Field(description="Why this makes university students laugh and share with their friends.")
    reference_video_search_query: str = Field(
        description="Search query to see the original viral trend video format."
    )
    reference_video_url: str = Field(
        default="",
        description="Link to watch an example of this format.",
    )


class ReelPack(BaseModel):
    ideas: List[ReelIdea]


class CampaignPost(BaseModel):
    format: Literal["Reel", "Carousel", "Story", "Static Post", "Collab Post", "Live"]
    idea: str
    caption_draft: str


class CampaignPhase(BaseModel):
    name: str = Field(description="e.g. 'Teaser / Meme Hype', 'Countdown', 'Event Day', 'Recap & Bloopers'.")
    timing: str = Field(description="When, relative to the event.")
    goal: str
    posts: List[CampaignPost]


class Campaign(BaseModel):
    campaign_name: str
    big_idea: str = Field(description="The central entertaining concept tying everything together.")
    tagline: str
    phases: List[CampaignPhase]
    offline_ideas: List[str] = Field(description="Fun, engaging on-campus activities, photo booths, or interactive games.")
    collab_ideas: List[str] = Field(description="Societies, campus creators, or pages to collaborate with.")
    hashtags: List[str]
    kpis: List[str] = Field(description="Measurable goals.")


# --------------------------------------------------------------------------- #
# Society profile + containers
# --------------------------------------------------------------------------- #
@dataclass
class SocietyProfile:
    name: str = "University Society"
    niche: str = "General / Fun / Non-tech (Student Life & Memes)"
    university: str = ""
    region: str = "Pakistan"
    language: str = "English with some Roman Urdu"
    tones: List[str] = field(default_factory=lambda: ["Pure Comedy / Hilarious Memes", "Relatable student life"])
    extra_context: str = ""

    def to_prompt(self) -> str:
        lines = [
            f"- Society name: {self.name}",
            f"- Category / Focus: {self.niche}",
            f"- University: {self.university or 'not specified'}",
            f"- Country/region: {self.region}",
            f"- Target audience: university students and youth in {self.region}",
            f"- Caption language: {self.language}",
            f"- Preferred vibe & tone: {', '.join(self.tones) or 'Comedy & relatable'}",
        ]
        if self.extra_context.strip():
            lines.append(f"- Extra context: {self.extra_context.strip()}")
        return "\n".join(lines)


@dataclass
class Result:
    data: Any
    sources: List[dict] = field(default_factory=list)
    queries: List[str] = field(default_factory=list)
    signals_used: int = 0


SYSTEM_INSTRUCTION = (
    "You are a viral Gen-Z content creator and meme master who makes genuinely funny, "
    "highly shareable Instagram Reels for university societies. "
    "Rules for your comedy and suggestions: "
    "1. FOCUS ON PURE RELATABILITY & HUMOR: Cafeteria drama, university attendance, exams, waking up for 8am class, "
    "society drama, pretending to work, friendship, canteen gossip, professors, group project freeloaders. "
    "2. DO NOT make it technical or tech-heavy unless explicitly requested. Avoid boring corporate/academic talk. "
    "3. Keep jokes campus-friendly and respectful (no offensive, political, or vulgar content), but make them truly funny. "
    "4. For EVERY trend and reel, provide a realistic search query that users can search on Instagram/YouTube/TikTok "
    "to immediately watch the viral format video visually."
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def make_client(api_key: Optional[str] = None) -> genai.Client:
    return genai.Client(api_key=api_key) if api_key else genai.Client()


def _today() -> str:
    return dt.date.today().strftime("%A, %d %B %Y")


def _json_schema(model: Type[BaseModel]) -> dict:
    schema = model.model_json_schema()
    defs = schema.pop("$defs", {})

    def resolve(node: Any) -> Any:
        if isinstance(node, dict):
            if "$ref" in node:
                return resolve(copy.deepcopy(defs[node["$ref"].split("/")[-1]]))
            return {k: resolve(v) for k, v in node.items()}
        if isinstance(node, list):
            return [resolve(x) for x in node]
        return node

    return resolve(schema)


def _clean_json(text: str) -> str:
    text = (text or "").strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    return fence.group(1) if fence else text


def build_video_search_url(query: str, platform: str = "instagram") -> str:
    """Build a search URL so user can click and visually see the trend video."""
    q = quote_plus(query.strip())
    if platform == "youtube":
        return f"https://www.youtube.com/results?search_query={q}"
    # Instagram web search
    return f"https://www.instagram.com/explore/tags/{quote_plus(re.sub(r'[^a-zA-Z0-9]', '', query))}/" if " " not in query else f"https://www.google.com/search?q={q}+instagram+reels&tbm=vid"


def attach_video_links(data: Any) -> None:
    """Ensure every trend and reel has working direct search video links."""
    if hasattr(data, "trends"):
        for t in data.trends:
            if not t.reference_video_url or "http" not in t.reference_video_url:
                q = t.reference_video_search_query or t.name
                t.reference_video_url = f"https://www.google.com/search?q={quote_plus(q + ' instagram reels')}&tbm=vid"
    elif hasattr(data, "ideas"):
        for r in data.ideas:
            if not r.reference_video_url or "http" not in r.reference_video_url:
                q = r.reference_video_search_query or r.trend_used or r.title
                r.reference_video_url = f"https://www.google.com/search?q={quote_plus(q + ' instagram reel audio trend')}&tbm=vid"


def _extract_grounding(interaction: Any) -> tuple[List[dict], List[str]]:
    sources: dict[str, str] = {}
    queries: List[str] = []
    for step in getattr(interaction, "steps", None) or []:
        stype = getattr(step, "type", None)
        if stype == "google_search_call":
            args = getattr(step, "arguments", None)
            q = args.get("queries") if isinstance(args, dict) else getattr(args, "queries", None)
            queries.extend(q or [])
        elif stype == "model_output":
            for block in getattr(step, "content", None) or []:
                for ann in getattr(block, "annotations", None) or []:
                    url = getattr(ann, "url", None)
                    if getattr(ann, "type", None) == "url_citation" and url:
                        sources.setdefault(url, getattr(ann, "title", None) or url)
    return [{"title": t, "url": u} for u, t in sources.items()], queries


def _friendly_error(err: Exception) -> RuntimeError:
    msg = str(err)
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
        return RuntimeError(
            "Gemini Free Tier quota limit reached (HTTP 429).\n\n"
            "Quick fixes:\n"
            "1. Leave 'Use Google Search grounding' UNCHECKED in the sidebar.\n"
            "2. Wait 30-60 seconds and try again (free tier allows up to 15 requests per minute).\n"
            "3. If this key has been heavily used today, generate a fresh key at https://aistudio.google.com/apikey"
        )
    return RuntimeError(f"Gemini error: {err}")


def _run(
    client: genai.Client,
    prompt: str,
    schema: Type[T],
    enable_grounding: bool = False,
    extra_sources: Optional[List[dict]] = None,
    signals_count: int = 0,
) -> Result:
    response_format = {
        "type": "text",
        "mime_type": "application/json",
        "schema": _json_schema(schema),
    }
    tools = [{"type": "google_search"}] if enable_grounding else None

    last_err: Optional[Exception] = None
    for model_name in FALLBACK_MODELS:
        try:
            kwargs: dict[str, Any] = {
                "model": model_name,
                "system_instruction": SYSTEM_INSTRUCTION,
                "input": prompt,
                "response_format": response_format,
            }
            if tools:
                kwargs["tools"] = tools

            interaction = client.interactions.create(**kwargs)
            data = schema.model_validate_json(_clean_json(interaction.output_text))
            attach_video_links(data)
            sources, queries = _extract_grounding(interaction) if tools else ([], [])
            if extra_sources:
                sources = (extra_sources or []) + sources
            return Result(data, sources, queries, signals_used=signals_count)
        except Exception as err:
            if "429" in str(err) or "RESOURCE_EXHAUSTED" in str(err):
                raise _friendly_error(err) from err
            last_err = err
            continue

    if last_err:
        raise _friendly_error(last_err) from last_err
    raise RuntimeError("Failed to generate content with any model.")


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
TREND_FOCUS = {
    "Funny memes & relatable student humor": "viral memes, relatable student life moments, hilarious campus situations, funny POVs",
    "Viral audios & sounds": "trending funny sounds, comedic audio clips, dialogue voiceovers",
    "POV & funny skit formats": "relatable POV templates, unexpected punchline skits, acting formats",
    "Pakistani / Desi campus humor": "desi student struggles, chai breaks, attendance shortages, exam tension, Pakistani university banter",
    "Challenges & trend templates": "funny challenges, photo drops, team banter templates",
}


def find_trends(
    client: genai.Client,
    profile: SocietyProfile,
    focus: str,
    count: int,
    enable_grounding: bool = False,
) -> Result:
    signals = fetchers.collect_live_signals(region=profile.region, niche=profile.niche)
    signals_prompt = fetchers.signals_to_prompt(signals)
    extra_sources = [{"title": f"[{s.source}] {s.title}", "url": s.url} for s in signals if s.url]

    prompt = f"""Today is {_today()}.

Find the {count} funniest, most viral CURRENT Instagram Reels trends for this university society,
focusing on: {TREND_FOCUS.get(focus, focus)}.

Society profile:
{profile.to_prompt()}

{signals_prompt}

IMPORTANT RULES:
- PRIORITIZE GENUINE HUMOR: Make the ideas actually funny, relatable, and entertaining for university students.
- DO NOT force tech or technical topics unless the user explicitly requested it. Focus on general campus life, student humor, funny situations, and viral meme audio trends.
- For EVERY trend, include a `reference_video_search_query` that clearly specifies how to search and see the exact viral reel format (e.g., 'instagram reel audio wait for it meme', 'tiktok pov student late to class format').
- Make sure at least 2 trends are local to {profile.region} (e.g. Desi campus culture, university attendance panic, canteen banter).
"""
    return _run(
        client,
        prompt,
        TrendReport,
        enable_grounding=enable_grounding,
        extra_sources=extra_sources,
        signals_count=len(signals),
    )


def generate_reel_ideas(
    client: genai.Client,
    profile: SocietyProfile,
    count: int,
    theme: str = "",
    trend: Optional[Trend] = None,
    enable_grounding: bool = False,
) -> Result:
    if trend:
        trend_part = (
            f"Build every funny idea on this trend:\n{trend.name} ({trend.category}) - "
            f"{trend.description}\nWhy it's funny: {trend.why_funny}\n"
            f"Suggested adaptation: {trend.how_to_adapt}"
        )
        signals = []
    else:
        signals = fetchers.collect_live_signals(region=profile.region, niche=profile.niche)
        trend_part = (
            "Base each reel on a DIFFERENT funny viral trend or meme format popular right now on Instagram/TikTok.\n"
            + fetchers.signals_to_prompt(signals[:10])
        )

    prompt = f"""Today is {_today()}.

Create {count} hilarious, ready-to-film Instagram Reel scripts for university students.

Society profile:
{profile.to_prompt()}

Reel objective / theme: {theme.strip() or "pure fun, viral student engagement, relatable comedy"}

{trend_part}

RULES:
- Focus on RELATABLE COMEDY, meme acting, funny expressions, and unexpected twists.
- Do NOT make it about boring technical lectures or tech jargon unless explicitly asked.
- Each reel must be easily filmed on a phone by students on campus in 20-40 minutes.
- Give a strong hook in the first 2 seconds.
- Provide a `reference_video_search_query` for each reel so the user can look up the format visually on video.
- Best posting time must be for the {profile.region} timezone (PKT for Pakistan).
"""
    extra_sources = [{"title": f"[{s.source}] {s.title}", "url": s.url} for s in signals if s.url]
    return _run(
        client,
        prompt,
        ReelPack,
        enable_grounding=enable_grounding,
        extra_sources=extra_sources,
        signals_count=len(signals),
    )


def plan_campaign(
    client: genai.Client,
    profile: SocietyProfile,
    event_name: str,
    event_date: dt.date,
    event_type: str,
    details: str,
    goal: str,
    enable_grounding: bool = False,
) -> Result:
    days_left = (event_date - dt.date.today()).days
    prompt = f"""Today is {_today()}. The event is on {event_date:%A, %d %B %Y} ({days_left} days from now).

Plan a complete entertaining social media + on-campus marketing campaign for this event,
using funny, engaging Instagram Reel formats and marketing stunts.

Society profile:
{profile.to_prompt()}

Event:
- Name: {event_name}
- Type: {event_type}
- Details: {details or "not specified"}
- Main goal: {goal}

Rules:
- Make the marketing lively, humorous, and buzz-worthy (not stiff or boring corporate ads).
- Mix funny reels, interactive stories, meme countdowns, and fun campus activities.
- Offline ideas should be cheap and easy for student volunteers to pull off.
"""
    return _run(client, prompt, Campaign, enable_grounding=enable_grounding)
