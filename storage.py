"""Saving ideas to SQLite per user + converting them to shareable Markdown."""

from __future__ import annotations

import datetime as dt
import json
import sqlite3
import uuid
from pathlib import Path
from typing import List, Optional

import auth

DATA_FILE = Path(__file__).parent / "data" / "saved_ideas.json"


# --------------------------------------------------------------------------- #
# Persistence (Per-User SQLite Database)
# --------------------------------------------------------------------------- #
def load_saved(user_id: Optional[str] = None) -> List[dict]:
    """Load saved trends, reels, and campaigns for a specific user."""
    auth.init_db()
    uid = user_id or "guest"

    try:
        with auth.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, kind, title, data_json, saved_at
                FROM saved_ideas
                WHERE user_id = ?
                ORDER BY saved_at DESC
                """,
                (uid,),
            ).fetchall()

            if rows:
                results = []
                for r in rows:
                    try:
                        results.append(
                            {
                                "id": r["id"],
                                "kind": r["kind"],
                                "saved_at": r["saved_at"],
                                "data": json.loads(r["data_json"]),
                            }
                        )
                    except json.JSONDecodeError:
                        continue
                return results
    except Exception:
        pass

    # Fallback to local JSON only if no specific user ID is provided (legacy guest mode)
    if not user_id and DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def save_item(kind: str, data: dict, user_id: Optional[str] = None) -> str:
    """Save a trend, reel, or campaign tied to the user's account."""
    auth.init_db()
    uid = user_id or "guest"
    item_id = uuid.uuid4().hex[:8]
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    title = (
        data.get("name")
        or data.get("title")
        or data.get("campaign_name")
        or f"Saved {kind}"
    )

    try:
        with auth.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO saved_ideas (id, user_id, kind, title, data_json, saved_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (item_id, uid, kind, title, json.dumps(data, ensure_ascii=False), now),
            )
            conn.commit()
    except Exception:
        # Fallback to JSON
        items = []
        if DATA_FILE.exists():
            try:
                items = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            except Exception:
                items = []
        items.insert(0, {"id": item_id, "kind": kind, "saved_at": now, "data": data})
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

    return item_id


def delete_item(item_id: str, user_id: Optional[str] = None) -> None:
    """Delete a saved item belonging to the user."""
    auth.init_db()
    uid = user_id or "guest"
    try:
        with auth.get_connection() as conn:
            conn.execute(
                "DELETE FROM saved_ideas WHERE id = ? AND (user_id = ? OR user_id = 'guest')",
                (item_id, uid),
            )
            conn.commit()
    except Exception:
        pass

    if DATA_FILE.exists():
        try:
            items = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            items = [i for i in items if i.get("id") != item_id]
            DATA_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# Markdown export (for sharing in WhatsApp / Notion / Google Docs)
# --------------------------------------------------------------------------- #
def trend_md(t: dict) -> str:
    video_link = (
        f"[Watch Example Video ({t.get('reference_video_search_query', 'Watch')})]({t.get('reference_video_url')})"
        if t.get("reference_video_url")
        else ""
    )
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
        for s in r.get("shot_list", [])
    )
    video_link = (
        f"[Watch Example Trend Video]({r.get('reference_video_url')})"
        if r.get("reference_video_url")
        else ""
    )
    return (
        f"### 🎬 {r['title']}\n"
        f"*Trend: {r['trend_used']} · {r['duration_seconds']}s · Comedy & Virality: {r['virality_score']}/10*\n\n"
        f"**Hook:** {r['hook']}\n\n"
        f"**Concept:** {r['concept']}\n\n"
        f"**Watch Format Example:** {video_link}\n\n"
        f"| Time | Visual | Text overlay | Voiceover |\n|---|---|---|---|\n{shots}\n\n"
        f"**Audio:** {r['audio_suggestion']}\n\n"
        f"**Props:** {', '.join(r.get('props_needed', [])) or '—'}\n\n"
        f"**Post at:** {r['best_posting_time']}\n\n"
        f"**Caption:**\n\n{r['caption']}\n\n"
        f"{' '.join(r.get('hashtags', []))}\n\n"
        f"**Why it works:** {r['why_it_works']}\n"
    )


def campaign_md(c: dict) -> str:
    out = [
        f"## 📣 {c['campaign_name']}",
        f"**Tagline:** {c['tagline']}",
        f"**Big idea:** {c['big_idea']}",
    ]
    for p in c.get("phases", []):
        out.append(f"\n### {p['name']} — {p['timing']}\n*Goal: {p['goal']}*")
        for post in p.get("posts", []):
            out.append(f"- **{post['format']}:** {post['idea']}\n  - Caption: {post['caption_draft']}")
    out.append("\n### On-campus ideas\n" + "\n".join(f"- {x}" for x in c.get("offline_ideas", [])))
    out.append("\n### Collab ideas\n" + "\n".join(f"- {x}" for x in c.get("collab_ideas", [])))
    out.append("\n### KPIs\n" + "\n".join(f"- {x}" for x in c.get("kpis", [])))
    out.append("\n" + " ".join(c.get("hashtags", [])))
    return "\n".join(out)


def to_markdown(kind: str, data: dict) -> str:
    return {"trend": trend_md, "reel": reel_md, "campaign": campaign_md}[kind](data)
