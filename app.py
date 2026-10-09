"""TrendScout — trending Instagram Reel ideas for university societies.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import datetime as dt
import os
from urllib.parse import quote_plus

import streamlit as st
from dotenv import load_dotenv

import storage
from theme import LOGOS, THEME_CFG, get_css
from trends import (
    TREND_FOCUS,
    Result,
    SocietyProfile,
    find_trends,
    generate_reel_ideas,
    make_client,
    plan_campaign,
)

load_dotenv()

st.set_page_config(page_title="TrendScout Studio", page_icon="🎬", layout="wide")

# Locked Theme: Monolith (Pure Pitch Black)
logo_svg = LOGOS["monolith"]

# Inject Monolith CSS directly
st.markdown(get_css(), unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# Sidebar: Branding & Profile
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown(
        f'<div class="brand-header">{logo_svg}<div><h2 class="brand-title">TrendScout</h2><div class="brand-sub">University Society Reels Studio</div></div></div>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.subheader("Society Profile")
    profile = SocietyProfile(
        name=st.text_input("Society name", "Youth & Events Society"),
        niche=st.selectbox(
            "Society Category / Focus",
            [
                "General / Fun / Non-tech (Student Life & Memes)",
                "Arts, Drama & Media Society",
                "Sports & Adventure Club",
                "Social Welfare & Volunteer Club",
                "Literary & Debating Society",
                "Music & Performing Arts",
                "Tech / Coding (Optional)",
            ],
            index=0,
            help="Pick 'General / Fun / Non-tech' if you want pure entertainment, campus memes, and relatable student life without technical jargon.",
        ),
        university=st.text_input("University", placeholder="e.g. NUST, FAST, LUMS, GIKI, IBA, COMSATS"),
        region=st.text_input("Country / region", "Pakistan"),
        language=st.selectbox(
            "Caption & dialogue language",
            ["English with some Roman Urdu", "Roman Urdu & English mix", "English only", "Urdu"],
        ),
        tones=st.multiselect(
            "Comedy & content tone",
            [
                "Pure Comedy / Hilarious Memes",
                "Relatable student life",
                "Sarcastic / Witty banter",
                "Hype / High energy",
                "Wholesome & heartwarming",
                "Cinematic & aesthetic",
            ],
            default=["Pure Comedy / Hilarious Memes", "Relatable student life"],
        ),
        extra_context=st.text_area(
            "Inside jokes & extra context",
            placeholder="e.g. 8am classes, canteen samosas, strict attendance rule, exam season stress, society president drama...",
        ),
    )

# Main Banner with Cyber Reel Logo
st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 16px; margin: 8px 0 24px 0;">
      {logo_svg}
      <div>
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px;">TrendScout Studio</h1>
        <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.95rem;">
          Find viral trends, funny campus reel ideas, and watch real video examples for <b>{profile.name}</b>
        </p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

STATUS_ICON = {"Rising": "📈", "Peak": "🔥", "Fading": "📉"}


def get_client():
    # User custom key entered in Settings tab takes highest priority
    custom_key = st.session_state.get("custom_api_key", "").strip()
    if custom_key:
        return make_client(custom_key)

    # Otherwise read from environment (.env) or Streamlit Cloud Secrets (st.secrets)
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    if not api_key:
        st.error(
            "Gemini API key not found! Please open the **⚙️ Settings / API Key** tab to enter your key, "
            "or set GEMINI_API_KEY in Streamlit Cloud Secrets / .env file."
        )
        st.stop()
    return make_client(api_key)


def show_sources(result: Result) -> None:
    if result.signals_used:
        st.caption(
            f"⚡ Powered by **{result.signals_used} live web signals** (Google Trends PK, Reddit memes & community trends)"
        )
    if result.sources or result.queries:
        with st.expander(f"🔎 Sources & live references ({len(result.sources)})"):
            if result.queries:
                st.caption("Searches run: " + " · ".join(f"`{q}`" for q in result.queries))
            for s in result.sources:
                if s.get("url"):
                    st.markdown(f"- [{s['title']}]({s['url']})")
                else:
                    st.markdown(f"- {s['title']}")


def save_button(kind: str, data: dict, key: str) -> None:
    if st.button("⭐ Save Idea", key=key):
        storage.save_item(kind, data)
        st.toast("Saved! Find it in the ⭐ Saved tab.")


# --------------------------------------------------------------------------- #
# Tabs
# --------------------------------------------------------------------------- #
tab_trends, tab_reels, tab_campaign, tab_saved, tab_settings = st.tabs(
    ["🔥 Trend Radar", "🎬 Reel Ideas", "📣 Campaign Planner", "⭐ Saved", "⚙️ Settings / API Key"]
)

# Tab hover tooltips
st.markdown(
    """
    <script>
    const tabTooltips = [
      "🔥 Trend Radar — Live viral formats, memes & sounds",
      "🎬 Reel Ideas — Ready-to-film comedic scripts & shot lists",
      "📣 Campaign Planner — Event marketing campaigns & campus stunts",
      "⭐ Saved — Your saved trends, scripts & exported ideas",
      "⚙️ Settings — Optional Gemini API key override"
    ];
    function attachTooltips() {
      const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
      tabs.forEach((tab, i) => {
        if (tabTooltips[i]) {
          tab.setAttribute('title', tabTooltips[i]);
        }
      });
    }
    attachTooltips();
    setTimeout(attachTooltips, 500);
    setTimeout(attachTooltips, 1500);
    </script>
    """,
    unsafe_allow_html=True,
)

# ---------------------------- Trend Radar ---------------------------------- #
with tab_trends:
    st.subheader("What's making people laugh right now?")
    st.caption("Pulls trending comedic formats, viral audios, and memes, and adapts them into funny campus reels.")

    c1, c2 = st.columns([2, 1])
    focus = c1.selectbox("Filter trend style", list(TREND_FOCUS.keys()))
    count = c2.slider("Number of trends to show", 4, 10, 6)

    if st.button("🔍 Find funny trends", type="primary"):
        with st.spinner("Finding hilarious viral trends & creating adaptations…"):
            try:
                st.session_state["trends"] = find_trends(
                    get_client(), profile, focus, count, enable_grounding=enable_grounding
                )
            except Exception as e:
                st.error(str(e))

    result: Result | None = st.session_state.get("trends")
    if result:
        st.info(result.data.overview)
        for i, t in enumerate(result.data.trends):
            with st.container(border=True):
                st.markdown(f"#### {STATUS_ICON.get(t.status, '')} {t.name}")
                st.markdown(
                    f"<span class='badge'>{t.category}</span>"
                    f"<span class='badge badge-accent'>{t.region}</span>"
                    f"<span class='badge'>{t.status}</span>"
                    f"<span class='badge badge-accent'>Filming Effort: {t.effort}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**What the trend is:** {t.description}")
                st.markdown(f"**😂 Why it's funny / The Joke:** {t.why_funny}")
                st.markdown(f"**💡 How your society can adapt it:** {t.how_to_adapt}")
                st.markdown(f"<div class='hook'>Opening Hook: “{t.example_hook}”</div>", unsafe_allow_html=True)

                search_query = getattr(t, "reference_video_search_query", t.name)
                video_url = getattr(t, "reference_video_url", "")
                if not video_url:
                    video_url = f"https://www.google.com/search?q={quote_plus(search_query + ' instagram reels')}&tbm=vid"
                yt_url = f"https://www.youtube.com/results?search_query={quote_plus(search_query)}"

                st.markdown(
                    f"""
                    <div class="video-link-box">
                      👀 <b>Watch how this trend looks on video:</b><br/>
                      👉 <a href="{video_url}" target="_blank"><b>Watch Video Example (Instagram / Web)</b></a> &nbsp;|&nbsp;
                      👉 <a href="{yt_url}" target="_blank"><b>Watch on YouTube Shorts</b></a>
                      <br/><small style="color:#94A3B8;">Search query: <i>"{search_query}"</i></small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                b1, b2, _ = st.columns([1.5, 1, 4])
                if b1.button("🎬 Make a reel script from this", key=f"use_trend_{i}"):
                    st.session_state["selected_trend"] = t
                    st.toast(f"Selected '{t.name}'. Open the 🎬 Reel Ideas tab!")
                with b2:
                    save_button("trend", t.model_dump(), f"save_trend_{i}")
        show_sources(result)

# ---------------------------- Reel Ideas ----------------------------------- #
with tab_reels:
    st.subheader("Funny, Ready-to-Film Reel Scripts")

    selected = st.session_state.get("selected_trend")
    if selected:
        c1, c2 = st.columns([5, 1])
        c1.success(f"Using trend: **{selected.name}** ({selected.category})")
        if c2.button("✖ Clear"):
            st.session_state.pop("selected_trend")
            st.rerun()
    else:
        st.caption("Tip: Pick a trend in 🔥 Trend Radar, or let the AI pick pure comedy trends for you.")

    c1, c2 = st.columns([3, 1])
    theme = c1.text_input(
        "What is the reel about? (optional)",
        placeholder="e.g. Society recruitment, hostel vs day-scholar humor, exam time panic, canteen gossip...",
    )
    n_ideas = c2.slider("Number of ideas", 1, 5, 3)

    if st.button("✨ Generate funny reel scripts", type="primary"):
        with st.spinner("Writing hilarious reel scripts with shot-by-shot lists…"):
            try:
                st.session_state["reels"] = generate_reel_ideas(
                    get_client(),
                    profile,
                    n_ideas,
                    theme,
                    selected,
                    enable_grounding=enable_grounding,
                )
            except Exception as e:
                st.error(str(e))

    result = st.session_state.get("reels")
    if result:
        all_md = "\n\n---\n\n".join(storage.reel_md(r.model_dump()) for r in result.data.ideas)
        st.download_button("⬇️ Download all as Markdown", all_md, "funny_reel_ideas.md", "text/markdown")

        for i, r in enumerate(result.data.ideas):
            with st.container(border=True):
                st.markdown(f"### 😂 {r.title}")
                st.markdown(
                    f"<span class='badge'>Trend: {r.trend_used}</span>"
                    f"<span class='badge badge-accent'>{r.duration_seconds}s</span>"
                    f"<span class='badge'>Comedy & Shareability: {r.virality_score}/10</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"<div class='hook'>🪝 Hook: {r.hook}</div>", unsafe_allow_html=True)
                st.markdown(f"**Premise / Joke:** {r.concept}")

                search_q = getattr(r, "reference_video_search_query", r.trend_used or r.title)
                v_url = getattr(r, "reference_video_url", "")
                if not v_url:
                    v_url = f"https://www.google.com/search?q={quote_plus(search_q + ' instagram reel audio trend')}&tbm=vid"
                yt_q_url = f"https://www.youtube.com/results?search_query={quote_plus(search_q)}"

                st.markdown(
                    f"""
                    <div class="video-link-box">
                      👀 <b>Visual Reference (Watch how other creators perform this):</b><br/>
                      👉 <a href="{v_url}" target="_blank"><b>Watch Video Example on Instagram / Web</b></a> &nbsp;|&nbsp;
                      👉 <a href="{yt_q_url}" target="_blank"><b>Watch Video on YouTube Shorts</b></a>
                      <br/><small style="color:#94A3B8;">Search term: <i>"{search_q}"</i></small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("**🎥 Shot-by-Shot Acting & Camera Guide**")
                st.dataframe(
                    [
                        {
                            "Time": s.seconds,
                            "What to film & Facial Expressions": s.visual,
                            "Text on Screen": s.text_overlay,
                            "Spoken Line / Dialogue / Audio": s.voiceover,
                        }
                        for s in r.shot_list
                    ],
                    hide_index=True,
                    width="stretch",
                )

                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**🎵 Trending Audio / Sound**\n\n{r.audio_suggestion}")
                c2.markdown(f"**🕒 Best Time to Post**\n\n{r.best_posting_time}")
                c3.markdown("**🧰 Simple Props Needed**\n\n" + (", ".join(r.props_needed) or "Phone only"))

                st.markdown("**📝 Instagram Caption (Click top right to copy)**")
                st.code(r.caption + "\n\n" + " ".join(r.hashtags), language=None, wrap_lines=True)
                st.markdown(f"**Why this works & gets shares:** {r.why_it_works}")
                save_button("reel", r.model_dump(), f"save_reel_{i}")
        show_sources(result)

# ---------------------------- Campaign Planner ----------------------------- #
with tab_campaign:
    st.subheader("Entertaining Event Marketing Campaign")
    st.caption("Plan teasers, funny countdowns, memes, campus stunts and hype for your upcoming event.")

    c1, c2, c3 = st.columns([2, 1, 1])
    event_name = c1.text_input("Event name", placeholder="e.g. Annual Campus Fest, Welcome Party, Sports Week, Drama Night")
    event_date = c2.date_input("Event date", dt.date.today() + dt.timedelta(days=21))
    event_type = c3.selectbox(
        "Event Type",
        [
            "Social / Fun Fest / Concert",
            "Welcome Party / Farewell",
            "Sports Tournament / Gaming",
            "Drama / Cultural Night",
            "Recruitment Drive",
            "Workshop / Seminar",
            "Competition",
        ],
    )
    details = st.text_area(
        "Event Details (optional)",
        placeholder="Ticket prices, venue, special guests, activities, food stalls, dress code...",
    )
    goal = st.selectbox(
        "Main Goal",
        [
            "Build massive campus hype & sell tickets",
            "Maximise attendance & engagement",
            "Recruit maximum new members",
            "Grow Instagram followers with funny content",
            "Attract sponsors & campus partners",
        ],
    )

    if st.button("🚀 Plan Entertaining Campaign", type="primary", disabled=not event_name):
        with st.spinner("Planning your event marketing campaign…"):
            try:
                st.session_state["campaign"] = plan_campaign(
                    get_client(),
                    profile,
                    event_name,
                    event_date,
                    event_type,
                    details,
                    goal,
                    enable_grounding=enable_grounding,
                )
            except Exception as e:
                st.error(str(e))

    result = st.session_state.get("campaign")
    if result:
        c = result.data
        st.subheader(f"📣 {c.campaign_name}")
        st.markdown(f"<div class='hook'>{c.tagline}</div>", unsafe_allow_html=True)
        st.markdown(f"**Big Idea:** {c.big_idea}")

        for p in c.phases:
            with st.expander(f"**{p.name}** — {p.timing}", expanded=True):
                st.caption(f"Goal: {p.goal}")
                for post in p.posts:
                    st.markdown(
                        f"<span class='badge badge-accent'>{post.format}</span> {post.idea}",
                        unsafe_allow_html=True,
                    )
                    st.code(post.caption_draft, language=None, wrap_lines=True)

        c1, c2, c3 = st.columns(3)
        c1.markdown("**🏫 Fun On-Campus Activities & Stunts**\n" + "\n".join(f"- {x}" for x in c.offline_ideas))
        c2.markdown("**🤝 Collab Ideas**\n" + "\n".join(f"- {x}" for x in c.collab_ideas))
        c3.markdown("**📊 KPIs to Track**\n" + "\n".join(f"- {x}" for x in c.kpis))
        st.code(" ".join(c.hashtags), language=None, wrap_lines=True)

        b1, b2, _ = st.columns([1.3, 1, 4])
        b1.download_button(
            "⬇️ Download Plan", storage.campaign_md(c.model_dump()), "campaign_plan.md", "text/markdown"
        )
        with b2:
            save_button("campaign", c.model_dump(), "save_campaign")
        show_sources(result)

# ---------------------------- Saved ---------------------------------------- #
with tab_saved:
    st.subheader("Saved Ideas")
    items = storage.load_saved()
    if not items:
        st.caption("Nothing saved yet. Hit ⭐ Save Idea on any trend, reel or campaign.")
    else:
        kinds = st.multiselect(
            "Filter saved items", ["trend", "reel", "campaign"], default=["trend", "reel", "campaign"]
        )
        items = [i for i in items if i["kind"] in kinds]
        export = "\n\n---\n\n".join(storage.to_markdown(i["kind"], i["data"]) for i in items)
        st.download_button("⬇️ Export All as Markdown", export, "saved_ideas.md", "text/markdown")

        icons = {"trend": "🔥", "reel": "🎬", "campaign": "📣"}
        for item in items:
            title = (
                item["data"].get("name")
                or item["data"].get("title")
                or item["data"].get("campaign_name")
            )
            with st.expander(f"{icons[item['kind']]} {title}  ·  {item['saved_at']}"):
                st.markdown(storage.to_markdown(item["kind"], item["data"]))
                if st.button("🗑️ Delete", key=f"del_{item['id']}"):
                    storage.delete_item(item["id"])
                    st.rerun()

# ---------------------------- Settings / API Key --------------------------- #
with tab_settings:
    st.subheader("⚙️ Settings & API Configuration")
    st.caption("Optionally use your own Google Gemini API key if you want to override the default system key.")

    current_custom_key = st.session_state.get("custom_api_key", "")
    key_input = st.text_input(
        "Enter your personal Gemini API Key",
        value=current_custom_key,
        type="password",
        placeholder="AIzaSy...",
        help="You can get a free API key at https://aistudio.google.com/apikey",
    )

    c1, c2, _ = st.columns([1.5, 1.5, 3])
    if c1.button("💾 Save Key", type="primary"):
        st.session_state["custom_api_key"] = key_input.strip()
        st.success("Your API key has been saved for this session!")
        st.rerun()

    if c2.button("✖ Clear Key"):
        st.session_state.pop("custom_api_key", None)
        st.info("Custom key cleared! App will use default server key.")
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
        ### ℹ️ How API Keys Work:
        - **By default:** The app runs on the free system key configured in Streamlit Cloud Secrets.
        - **Personal Key Override:** If you enter your own key here, TrendScout will use your key for all requests in this session.
        - **Get a Free Key:** Visit [Google AI Studio](https://aistudio.google.com/apikey), click **Create API Key**, and paste it above.
        """
    )

