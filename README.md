# 🎬 TrendScout Studio

> **AI-Powered Viral Reels Strategist & Content Studio for University Societies & Campus Creators**

TrendScout Studio is an open-source, AI-driven social media trends intelligence engine designed specifically for university clubs, societies, and student media teams. It continuously monitors live web signals (Google Trends, Reddit meme communities, and platform updates) to generate ready-to-film, highly relatable campus comedy reels, structured shot-by-shot production scripts, and comprehensive event marketing campaigns.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Model-Gemini%203.8%20Flash-8E75C4.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Theme](https://img.shields.io/badge/Theme-Monolith%20Pitch%20Black-000000.svg)](#design-identity)

> 📹 **Walkthrough Demo Video (38s):** [Watch `demo_walkthrough.mp4`](demo_walkthrough.mp4) to see the Sign Up, Login, Trend Radar, Reel Generator, and Multi-Device SQLite sync in action!

---

## ⚡ Features & Capabilities

| Module | Purpose | Key Outputs |
|---|---|---|
| **🔥 Trend Radar** | Live Cultural Trend Discovery | Synthesizes trending audios, viral POVs, campus memes, and local Pakistani/Desi student humor. Rates each trend by momentum (*Rising*, *Peak*, *Fading*) and production effort. |
| **👀 Visual References** | Video Learning & Direct Search | Every trend and script includes 1-click links to search and watch the real video format on **Instagram Reels**, **Google Videos**, and **YouTube Shorts**. |
| **🎬 Reel Ideas** | Ready-to-Film Scripts | Full shot-by-shot acting guides, visual descriptions, text overlays, spoken dialogue punchlines, virality ratings, props, captions, and peak posting times. |
| **📣 Campaign Planner** | Event Marketing Playbooks | Multi-phase promotional campaigns (Meme Teasers → Hype → Countdown → Event Day → Bloopers/Recap) with budget-friendly on-campus guerrilla stunts and measurable KPIs. |
| **🔐 Multi-User Auth** | Sign Up & Login System | Secure account creation with PBKDF2 password hashing. Saved trends and reel scripts sync to your account across multiple devices (phone, laptop, desktop). |
| **⭐ Idea Vault** | Persistence & Export | SQLite-backed per-user vault; export entire campaign packages into clean, shareable Markdown for WhatsApp groups, Notion, or team meetings. |
| **⚙️ Custom Key Override** | Multi-User Flexibility | Built-in settings tab allows visitors to supply their own Google Gemini API key or use the server's default configuration. |

---

## 🎨 Design Identity: Monolith Black

TrendScout is styled in a custom **Monolith** aesthetic:
- **OLED Pitch Black Canvas (`#000000`)** with subtle `#1F1F1F` hairline borders.
- **High-Contrast Frost White & Titanium Accents** for maximum readability and a premium VIP studio feel.
- **Custom Vector SVG Logo** embedded directly with no external image dependencies.
- **Interactive Tab Tooltips** providing quick feature previews on hover.

---

## 🛠️ Architecture & Tech Stack

- **Frontend & App Engine:** [Streamlit](https://streamlit.io/)
- **AI Core:** [Google Gemini 3.8 Flash](https://ai.google.dev/) via official `google-genai` SDK
- **Data Schemas & Type Safety:** [Pydantic v2](https://docs.pydantic.dev/) for strict schema validation
- **Live Signal Aggregation:** Asynchronous, keyless HTTP aggregators (`httpx`) pulling from Google Trends RSS, Reddit RSS, and developer feeds.
- **Styling:** Custom CSS injections with responsive flex layouts and SVG vector assets.

---

## 🚀 Quickstart & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/sufyanfiverr2-sketch/trend-scout.git
cd trend-scout
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your API key
Create a `.env` file from the example:
```bash
copy .env.example .env
```
Add your free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey):
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Launch the application
```bash
streamlit run app.py
```
Open **http://localhost:8501** in your browser.

---

## ☁️ Deployment to Streamlit Community Cloud

Deploy for free in 2 minutes:
1. Fork or push this repository to your GitHub account.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/).
3. Click **"New app"**, select `trend-scout`, branch `main`, and main file `app.py`.
4. In **Advanced Settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
5. Click **Deploy!**

---

## 📂 Repository Structure

```
trend-scout/
├── .streamlit/
│   └── config.toml      # Server headless config & Monolith dark theme defaults
├── data/                # Local saved ideas storage (git-ignored)
├── app.py               # Main Streamlit web application & UI tabs
├── trends.py            # AI prompting, Pydantic data models & Gemini orchestration
├── fetchers.py          # Keyless live trend aggregators (Google Trends, Reddit, Dev.to)
├── theme.py             # Monolith pitch-black CSS stylesheet & vector SVG logos
├── storage.py           # Local JSON persistence & Markdown exporter
├── requirements.txt     # Python dependency specifications
├── PROCESS.md           # Deep-dive technical architecture & workflow guide
├── .env.example         # Template for environment configuration
└── README.md            # Project documentation
```

---

## 📄 License

This project is licensed under the MIT License - feel free to use, modify, and distribute it for your university society or creative team.
