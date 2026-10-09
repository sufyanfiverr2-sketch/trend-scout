"""Saving ideas locally + converting them to shareable Markdown."""

from __future__ import annotations

import datetime as dt
import json
import uuid
from pathlib import Path
from typing import List

DATA_FILE = Path(__file__).parent / "data" / "saved_ideas.json"


# --------------------------------------------------------------------------- #
# Persistence
# --------------------------------------------------------------------------- #
def load_saved() -> List[dict]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _write(items: List[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def save_item(kind: str, data: dict) -> None:
    items = load_saved()
    items.insert(
        0,
        {
            "id": uuid.uuid4().hex[:8],
            "kind": kind,
            "saved_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "data": data,
        },
    )
    _write(items)


def delete_item(item_id: str) -> None:
    _write([i for i in load_saved() if i["id"] != item_id])


# --------------------------------------------------------------------------- #
# Markdown export (for sharing in WhatsApp / Notion / Google Docs)
# --------------------------------------------------------------------------- #
def trend_md(t: dict) -> str:
    video_link = f"[Watch Example Video ({t.get('reference_video_search_query', 'Watch')} )]({t.get('reference_video_url')})" if t.get("reference_video_url") else ""
    return (
        f"### 😂 {t['name']}\n"
        f"*{t['category']} · {t['region']} · {t['status']} · Effort: {t['effort']}*\n\n"
        f"**What it is:** {t['description']}\n\n"
        f"**Why it's funny:** {t.get('why_funny', '')}\n\n"
        f"**How to adapt for society:** {t['how_to_adapt']}\n\n"
        f"**Hook:** \"{t['example_hook']}\"\n\n"
        f"**Video Reference:** {video_link}\n"
    )


def reel_md(r: dict) -> str:
    shots = "\n".join(
        f"| {s['seconds']} | {s['visual']} | {s['text_overlay']} | {s['voiceover']} |"
        for s in r["shot_list"]
    )
    video_link = f"[Watch Example Trend Video]({r.get('reference_video_url')})" if r.get("reference_video_url") else ""
    return (
        f"### 🎬 {r['title']}\n"
        f"*Trend: {r['trend_used']} · {r['duration_seconds']}s · Comedy & Virality: {r['virality_score']}/10*\n\n"
        f"**Hook:** {r['hook']}\n\n"
        f"**Concept:** {r['concept']}\n\n"
        f"**Watch Format Example:** {video_link}\n\n"
        f"| Time | Visual | Text overlay | Voiceover |\n|---|---|---|---|\n{shots}\n\n"
        f"**Audio:** {r['audio_suggestion']}\n\n"
        f"**Props:** {', '.join(r['props_needed']) or '—'}\n\n"
        f"**Post at:** {r['best_posting_time']}\n\n"
        f"**Caption:**\n\n{r['caption']}\n\n"
        f"{' '.join(r['hashtags'])}\n\n"
        f"**Why it works:** {r['why_it_works']}\n"
    )


def campaign_md(c: dict) -> str:
    out = [
        f"## 📣 {c['campaign_name']}",
        f"**Tagline:** {c['tagline']}",
        f"**Big idea:** {c['big_idea']}",
    ]
    for p in c["phases"]:
        out.append(f"\n### {p['name']} — {p['timing']}\n*Goal: {p['goal']}*")
        for post in p["posts"]:
            out.append(f"- **{post['format']}:** {post['idea']}\n  - Caption: {post['caption_draft']}")
    out.append("\n### On-campus ideas\n" + "\n".join(f"- {x}" for x in c["offline_ideas"]))
    out.append("\n### Collab ideas\n" + "\n".join(f"- {x}" for x in c["collab_ideas"]))
    out.append("\n### KPIs\n" + "\n".join(f"- {x}" for x in c["kpis"]))
    out.append("\n" + " ".join(c["hashtags"]))
    return "\n".join(out)


def to_markdown(kind: str, data: dict) -> str:
    return {"trend": trend_md, "reel": reel_md, "campaign": campaign_md}[kind](data)
