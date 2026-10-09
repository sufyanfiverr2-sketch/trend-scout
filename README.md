# 🔥 TrendScout

An AI tool that finds **what's trending on Instagram Reels right now** and turns it into
ready-to-film ideas and marketing campaigns for a university society.

It uses **Gemini + Google Search grounding**, so the trends come from the live web, not
from old training data. Every result shows the sources it used.

## Features

| Tab | What it does |
|---|---|
| 🔥 **Trend Radar** | Current audios, formats, memes, challenges and tech topics, plus whether each one is rising or fading and how *your* society can use it |
| 🎬 **Reel Ideas** | Full scripts: hook, shot list, trending audio, caption, hashtags, best posting time, props, virality score |
| 📣 **Campaign Planner** | Phase-by-phase event marketing (teaser → hype → countdown → event day → recap), with on-campus stunts, collab ideas and KPIs |
| ⭐ **Saved** | Save your favourite ideas and export them as Markdown to share with the team |

## Setup

```powershell
cd d:\projects\trend-scout
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # then paste your key into .env
streamlit run app.py
```

Get a free Gemini API key at **https://aistudio.google.com/apikey**. You can also paste the key
straight into the sidebar instead of using `.env`.

## Tips
- Fill in **Extra context** in the sidebar (mascot, inside jokes, upcoming events). It makes the ideas much more specific.
- Flow: **Trend Radar → "Make reels from this" → Reel Ideas**.
- Re-run Trend Radar every week; trends change fast.

## Project structure
```
app.py       Streamlit UI
trends.py    Gemini calls, prompts and Pydantic schemas
storage.py   Saved ideas (data/saved_ideas.json) + Markdown export
```
