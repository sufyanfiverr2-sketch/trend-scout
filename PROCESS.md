# 📋 TrendScout Studio — Technical Process & Architecture Specification

This document details the end-to-end technical workflow, system design, data structures, and algorithms powering **TrendScout Studio**.

---

## 1. Executive Summary & Objective

TrendScout Studio bridges the gap between fast-moving cultural social media trends and university society marketing workflows. Standard LLM text generators suffer from stale knowledge cutoffs and lack real-world cultural context. TrendScout solves this through a hybrid architecture:
1. **Real-time, keyless web signal scraping** across search trends and community humor.
2. **Deterministic Pydantic validation** with structured JSON output enforcing shot-by-shot video scripts.
3. **Automated visual search query resolution** generating instant outbound query links to platforms like Instagram Reels and YouTube Shorts.

---

## 2. System Architecture

```
                    ┌────────────────────────────────────────────────────────┐
                    │               User Interface (Streamlit)               │
                    │  [Trend Radar] [Reel Ideas] [Campaigns] [Settings/Key] │
                    └───────────────────────────┬────────────────────────────┘
                                                │
                                    Triggers Analysis / Query
                                                ▼
┌─────────────────────────────────┐   Prompt Context   ┌─────────────────────────────────┐
│     Live Signal Aggregator      │ ─────────────────► │      Gemini 3.8 Flash Engine    │
│         (fetchers.py)           │                    │           (trends.py)           │
├─────────────────────────────────┤                    ├─────────────────────────────────┤
│ • Google Trends RSS (Geo: PK/US)│                    │ • System: Viral Gen-Z Strategist│
│ • Reddit RSS (r/memes, r/humor) │                    │ • Structured JSON Generation    │
│ • Hacker News & Dev.to APIs     │                    │ • Two-tier fallback parser      │
│ • Social Media Today Feeds      │                    │ • Direct Token Cost: Free Tier  │
└─────────────────────────────────┘                    └────────────────┬────────────────┘
                                                                        │
                                                               Typed Pydantic Schema
                                                                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               Data Enrichment Pipeline                                 │
│                                                                                        │
│  1. Inlines dynamic URL search strings for Instagram Reels & YouTube Shorts            │
│  2. Resolves virality potential, production difficulty, and posting timetables        │
│  3. Formats Markdown outputs and serializes to local JSON storage (storage.py)         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Technical Components & Modules

### 3.1 Live Signal Scraping (`fetchers.py`)
To avoid vendor lock-in and circumvent Google Gemini Search Grounding rate-limits ($14/1,000 queries, paid-tier only), `fetchers.py` collects live cultural signals using high-speed, keyless HTTP endpoints via `httpx`:
- **Google Trends RSS (`geo=PK` or `US`):** Parses XML Atom feeds (`trends.google.com/trending/rss`) extracting top 6 daily search queries and approximate search volume tags.
- **Reddit Atom Feeds:** Ingests top weekly posts from humor and marketing communities (`r/memes`, `r/wholesomememes`, `r/Instagrammarketing`, `r/ProgrammerHumor`) without requiring Reddit API credentials.
- **Developer & Tech Feeds:** Calls Algolia's public Hacker News search endpoint and the Dev.to REST API when technical niches are active.
- **Output:** Normalizes data into a strongly-typed `TrendSignal(source, title, context, url)` dataclass list.

### 3.2 AI Orchestration & Pydantic Validation (`trends.py`)
- **LLM Model:** `gemini-3.8-flash` via the official `google-genai` SDK (`interactions.create` endpoint).
- **Prompt Engineering:**
  - Instructs the model to act as a Gen-Z viral video strategist.
  - Enforces focus on non-technical, campus-relatable humor (attendance shortages, cafeteria culture, exam stress, society executive dynamics).
  - Injects timestamp context (`Today is Friday, 10 October 2026`) and current live signals to guarantee modern references.
- **Structured Outputs:**
  - Employs Pydantic v2 data models (`TrendReport`, `ReelPack`, `Campaign`).
  - Implements recursive schema un-nesting via `_json_schema()` to resolve JSON Schema `$defs` and `$ref` pointers, ensuring complete compatibility with the Gemini API response formatter.
- **Resilient Fallback Mechanism:**
  - Primary attempt: Strict JSON schema generation with tools disabled.
  - Secondary attempt: Plaintext research generation, followed by an immediate zero-tool restructuring pass if formatting errors occur.
  - Rate-limit interception: Catches HTTP 429 quota exceptions and displays user-friendly recovery instructions.

### 3.3 Visual Reference Link Builder
Creators often struggle to understand abstract written video concepts. To solve this, `trends.py` executes an automated reference resolver (`attach_video_links`):
1. The AI model returns an optimized search term (`reference_video_search_query`).
2. The system formats URL query components using `urllib.parse.quote_plus`:
   - **Instagram/Web Video:** `https://www.google.com/search?q={query}+instagram+reels&tbm=vid`
   - **YouTube Shorts:** `https://www.youtube.com/results?search_query={query}`
3. Users click directly to watch the viral format in action before filming.

### 3.4 Design & UI System (`theme.py` & `app.py`)
- **Monolith Theme:** True pitch-black (`#000000`) background with `#1C1C1C` borders and frost white accents (`#FFFFFF`).
- **BaseWeb & Emotion Tag Isolation:** Custom CSS rules targeting `.stMultiSelect [data-tag]`, `.e1kig3hy3`, and `.e1kig3hy4` ensuring high-contrast bold black text on crisp white multiselect pills.
- **Client Resilience:** Graceful handling of missing `st.secrets` files with automatic `.env` and session overrides.

### 3.5 Multi-User Authentication & Cross-Device Persistence (`auth.py` & `storage.py`)
- **Security:** Pure standard-library PBKDF2-HMAC-SHA256 key derivation with 100,000 iterations and per-user 16-byte random cryptographic salts (`secrets.token_hex(16)`).
- **Timing Defense:** Constant-time hash verification via `hmac.compare_digest` to mitigate timing analysis attacks.
- **Database Engine:** Embedded SQLite (`data/trendscout.db`) with foreign key constraints and indexed queries (`idx_users_username`, `idx_saved_ideas_user`).
- **Cross-Device Sync:** Saved trends, scripts, and campaign playbooks are bound to the authenticated `user_id`, enabling creators to bookmark ideas on mobile and review them later on desktop.
- **Guest Fallback:** Allows instant unauthenticated exploration with smooth in-app migration to full accounts.
- **Monolith Pure Pitch Black Palette:**
  - Background: `#000000` (Canvas) & `#080808` (Sidebar)
  - Cards: `#0A0A0A` with `#1F1F1F` borders
  - Primary Typography: `#FFFFFF` and `#F4F4F5`
  - Secondary/Accents: `#71717A` and `#E4E4E7`
- **Embedded SVG Vector Graphics:**
  - Zero external icon dependencies; renders lightweight SVG vectors directly in the DOM.
- **Dynamic JavaScript Tooltips:**
  - Injects non-intrusive client-side script listeners to populate `title` attributes across Streamlit's tab nodes (`data-baseweb="tab"`).

### 3.5 Persistence & Data Serialization (`storage.py`)
- Stores user-saved ideas into `data/saved_ideas.json` with unique UUIDs and timestamping.
- Translates structured records into standardized Markdown documentation ready for copy-pasting into Notion, Slack, or WhatsApp.

---

## 4. API Key Lifecycle & Security

1. **Hierarchy of Credentials:**
   - Priority 1: User-entered session key stored in `st.session_state["custom_api_key"]` (configured via the **⚙️ Settings** tab).
   - Priority 2: Server environment variable `GEMINI_API_KEY` (from `.env`).
   - Priority 3: Streamlit Community Cloud Secrets store (`st.secrets["GEMINI_API_KEY"]`).
2. **Data Safety:**
   - Keys supplied in the UI remain strictly inside browser session state and are never written to disk or pushed to GitHub.
   - `.gitignore` explicitly excludes `.env`, `.venv/`, `data/`, and all cache files.

---

## 5. Deployment Specs & Execution

| Parameter | Specification |
|---|---|
| Runtime | Python 3.10 – 3.14 |
| Target Platform | Streamlit Community Cloud (Debian Linux base container) |
| Port | `8501` (HTTP/WebSocket) |
| Configuration | Headless execution, CORS disabled, XSRF protection disabled for containerized proxies |
| Cost Profile | **$0.00 / month** (100% Free Tier compatible) |
