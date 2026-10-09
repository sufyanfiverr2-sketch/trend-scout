"""Theme definitions, custom SVG vector logos, and styling for TrendScout."""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Custom SVG Vector Logos (No cheap emojis)
# --------------------------------------------------------------------------- #
LOGOS = {
    "play_pulse": """
    <svg width="38" height="38" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="logoGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#FF385C" />
          <stop offset="50%" stop-color="#833AB4" />
          <stop offset="100%" stop-color="#405DE6" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="14" fill="url(#logoGrad1)" />
      <path d="M19 14L35 24L19 34V14Z" fill="white" />
      <circle cx="35" cy="15" r="3.5" fill="#FFDC80" />
    </svg>
    """,
    "radar_orbit": """
    <svg width="38" height="38" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="logoGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#6366F1" />
          <stop offset="100%" stop-color="#EC4899" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="14" fill="#0B0F19" stroke="url(#logoGrad2)" stroke-width="2" />
      <circle cx="24" cy="24" r="14" stroke="url(#logoGrad2)" stroke-width="2" stroke-dasharray="4 3" />
      <circle cx="24" cy="24" r="7" fill="url(#logoGrad2)" />
      <path d="M24 10V24L32 32" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" />
    </svg>
    """,
    "neon_spark": """
    <svg width="38" height="38" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="logoGrad3" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#10B981" />
          <stop offset="100%" stop-color="#06B6D4" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="14" fill="#0F172A" />
      <path d="M26 10L14 26H24L22 38L34 22H24L26 10Z" fill="url(#logoGrad3)" />
    </svg>
    """,
    "film_lens": """
    <svg width="38" height="38" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="logoGrad4" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#F59E0B" />
          <stop offset="100%" stop-color="#EF4444" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="14" fill="url(#logoGrad4)" />
      <rect x="11" y="14" width="26" height="20" rx="4" stroke="white" stroke-width="2.5" />
      <circle cx="24" cy="24" r="4.5" fill="white" />
      <path d="M15 14V19M33 14V19M15 29V34M33 29V34" stroke="white" stroke-width="2" />
    </svg>
    """
}

# --------------------------------------------------------------------------- #
# Theme Configurations
# --------------------------------------------------------------------------- #
THEMES = {
    "Cyber Reel (Neon Glow)": {
        "logo": "radar_orbit",
        "primary": "#8B5CF6",
        "secondary": "#EC4899",
        "accent": "#06B6D4",
        "badge_bg": "rgba(139, 92, 246, 0.15)",
        "badge_text": "#C4B5FD",
        "badge_border": "rgba(139, 92, 246, 0.4)",
        "hook_bg": "linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(236, 72, 153, 0.08))",
        "hook_border": "#A855F7",
        "box_bg": "rgba(15, 23, 42, 0.6)",
        "box_border": "rgba(148, 163, 184, 0.15)",
        "video_btn_bg": "linear-gradient(90deg, #7C3AED, #DB2777)",
        "tagline_color": "#A78BFA",
        "desc": "Modern dark aesthetic with neon violet & magenta accents. Great for contrast and high-energy feel.",
    },
    "Instagram Sunset (Viral Studio)": {
        "logo": "play_pulse",
        "primary": "#E1306C",
        "secondary": "#FD1D1D",
        "accent": "#FCAF45",
        "badge_bg": "rgba(225, 48, 108, 0.12)",
        "badge_text": "#F472B6",
        "badge_border": "rgba(225, 48, 108, 0.35)",
        "hook_bg": "linear-gradient(135deg, rgba(225, 48, 108, 0.12), rgba(252, 175, 69, 0.08))",
        "hook_border": "#E1306C",
        "box_bg": "rgba(24, 18, 28, 0.6)",
        "box_border": "rgba(225, 48, 108, 0.2)",
        "video_btn_bg": "linear-gradient(90deg, #E1306C, #F77737)",
        "tagline_color": "#FB7185",
        "desc": "Classic Instagram creator palette — vibrant berry pink, sunset orange, and gold.",
    },
    "Emerald Velocity (Clean & Crisp)": {
        "logo": "neon_spark",
        "primary": "#10B981",
        "secondary": "#06B6D4",
        "accent": "#34D399",
        "badge_bg": "rgba(16, 185, 129, 0.12)",
        "badge_text": "#6EE7B7",
        "badge_border": "rgba(16, 185, 129, 0.35)",
        "hook_bg": "linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(6, 182, 212, 0.08))",
        "hook_border": "#10B981",
        "box_bg": "rgba(6, 24, 20, 0.6)",
        "box_border": "rgba(16, 185, 129, 0.2)",
        "video_btn_bg": "linear-gradient(90deg, #059669, #0891B2)",
        "tagline_color": "#34D399",
        "desc": "Fresh, high-contrast mint green and cyan. Very clean, premium tech-society feel.",
    },
    "Sunset Cinema (Warm Creator)": {
        "logo": "film_lens",
        "primary": "#F59E0B",
        "secondary": "#EF4444",
        "accent": "#FBBF24",
        "badge_bg": "rgba(245, 158, 11, 0.14)",
        "badge_text": "#FCD34D",
        "badge_border": "rgba(245, 158, 11, 0.35)",
        "hook_bg": "linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(239, 68, 68, 0.08))",
        "hook_border": "#F59E0B",
        "box_bg": "rgba(28, 20, 10, 0.6)",
        "box_border": "rgba(245, 158, 11, 0.2)",
        "video_btn_bg": "linear-gradient(90deg, #D97706, #DC2626)",
        "tagline_color": "#FBBF24",
        "desc": "Film festival amber, warm gold, and bold crimson.",
    },
}


def get_css(theme_name: str) -> str:
    t = THEMES.get(theme_name, THEMES["Cyber Reel (Neon Glow)"])
    return f"""
    <style>
      /* Main Header Branding */
      .brand-header {{
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 4px;
      }}
      .brand-title {{
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        background: linear-gradient(90deg, #FFFFFF, {t['tagline_color']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }}
      .brand-sub {{
        font-size: 0.88rem;
        color: #94A3B8;
        margin-bottom: 18px;
      }}

      /* Modern Badge Styling */
      .badge {{
        display: inline-flex;
        align-items: center;
        padding: 3px 12px;
        margin: 0 6px 8px 0;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        background: {t['badge_bg']};
        color: {t['badge_text']};
        border: 1px solid {t['badge_border']};
      }}
      .badge-accent {{
        background: rgba(255, 255, 255, 0.08);
        color: #E2E8F0;
        border-color: rgba(255, 255, 255, 0.15);
      }}

      /* Hook Quote Box */
      .hook {{
        font-size: 1.05rem;
        font-weight: 700;
        line-height: 1.45;
        padding: 12px 16px;
        border-left: 4px solid {t['hook_border']};
        background: {t['hook_bg']};
        border-radius: 8px;
        margin: 10px 0 14px;
        color: #F8FAFC;
      }}

      /* Video Link Container */
      .video-link-box {{
        background: {t['box_bg']};
        border: 1px solid {t['box_border']};
        border-left: 4px solid {t['accent']};
        padding: 12px 16px;
        border-radius: 10px;
        margin: 12px 0;
      }}
      .video-link-box a {{
        color: {t['accent']} !important;
        text-decoration: none;
        font-weight: 600;
      }}
      .video-link-box a:hover {{
        text-decoration: underline;
      }}

      /* Primary Button enhancements */
      button[kind="primary"] {{
        background: {t['video_btn_bg']} !important;
        border: none !important;
        font-weight: 600 !important;
        letter-spacing: 0.2px !important;
      }}
    </style>
    """
