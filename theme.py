"""Theme definitions, custom SVG vector logos, and styling for TrendScout.
Monolith: Pure Pitch Black (#000000) with minimalist white, titanium, and silver accents.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Custom SVG Vector Logos (Minimalist Monolith Edition)
# --------------------------------------------------------------------------- #
LOGOS = {
    "monolith": """
    <svg width="38" height="38" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="monolithGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#FFFFFF" />
          <stop offset="100%" stop-color="#94A3B8" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="12" fill="#0D0D0D" stroke="#262626" stroke-width="1.5" />
      <path d="M19 14L34 24L19 34V14Z" fill="url(#monolithGrad)" />
      <circle cx="34" cy="15" r="3" fill="#FFFFFF" />
    </svg>
    """
}

THEME_CFG = {
    "logo": "monolith",
    "primary": "#FFFFFF",
    "secondary": "#A1A1AA",
    "accent": "#E4E4E7",
    "badge_bg": "rgba(255, 255, 255, 0.06)",
    "badge_text": "#E4E4E7",
    "badge_border": "rgba(255, 255, 255, 0.15)",
    "hook_bg": "linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02))",
    "hook_border": "#FFFFFF",
    "box_bg": "#0D0D0D",
    "box_border": "#222222",
    "video_btn_bg": "linear-gradient(180deg, #27272A, #18181B)",
    "tagline_color": "#D4D4D8",
    "desc": "Ultra-minimalist true pitch black with crisp frost white and titanium silver.",
}


def get_css() -> str:
    return """
    <style>
      /* Pure OLED Black Background Override */
      .stApp {
        background-color: #000000 !important;
        color: #F4F4F5 !important;
      }
      /* Header & Streamlit Developer Toolbar Removal */
      header[data-testid="stHeader"] {
        background-color: transparent !important;
      }
      #MainMenu,
      footer,
      [data-testid="stToolbar"],
      [data-testid="stToolbarActions"],
      [data-testid="stStatusWidget"],
      [data-testid="stDeployButton"],
      .stDeployButton,
      header[data-testid="stHeader"] a,
      header[data-testid="stHeader"] button[title*="Fork"],
      header[data-testid="stHeader"] button[aria-label*="Fork"],
      header[data-testid="stHeader"] [data-testid="stToolbarActions"],
      .viewerBadge_container__r5tak,
      .styles_viewerBadge__CvC9N,
      [data-testid="manage-app-button"],
      #manage-app-button {
        display: none !important;
        visibility: hidden !important;
      }
      section[data-testid="stSidebar"] {
        background-color: #080808 !important;
        border-right: 1px solid #1F1F1F !important;
      }

      /* Main Header Branding */
      .brand-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 4px;
      }
      .brand-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        background: linear-gradient(90deg, #FFFFFF, #A1A1AA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }
      .brand-sub {
        font-size: 0.88rem;
        color: #71717A;
        margin-bottom: 18px;
      }

      /* Monolith Badge Styling */
      .badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 12px;
        margin: 0 6px 8px 0;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        background: rgba(255, 255, 255, 0.06);
        color: #E4E4E7;
        border: 1px solid rgba(255, 255, 255, 0.16);
      }
      .badge-accent {
        background: rgba(255, 255, 255, 0.12);
        color: #FFFFFF;
        border-color: rgba(255, 255, 255, 0.28);
      }

      /* Hook Quote Box (Monolith Edition) */
      .hook {
        font-size: 1.05rem;
        font-weight: 700;
        line-height: 1.45;
        padding: 12px 16px;
        border-left: 4px solid #FFFFFF;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 6px;
        margin: 10px 0 14px;
        color: #FFFFFF;
      }

      /* Cards & Containers */
      div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #0A0A0A !important;
        border: 1px solid #1C1C1C !important;
        border-radius: 10px !important;
      }

      /* Video Link Container */
      .video-link-box {
        background: #0D0D0D;
        border: 1px solid #222222;
        border-left: 4px solid #FFFFFF;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
      }
      .video-link-box a {
        color: #FFFFFF !important;
        text-decoration: underline !important;
        font-weight: 600;
      }
      .video-link-box a:hover {
        color: #A1A1AA !important;
      }

      /* Buttons */
      button[kind="primary"] {
        background: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #FFFFFF !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px !important;
        border-radius: 6px !important;
        box-shadow: 0 2px 10px rgba(255, 255, 255, 0.15) !important;
        transition: all 0.15s ease !important;
      }
      button[kind="primary"]:hover {
        background: #E4E4E7 !important;
        color: #000000 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(255, 255, 255, 0.25) !important;
      }
      button[kind="secondary"] {
        background: #141414 !important;
        border: 1px solid #262626 !important;
        color: #E4E4E7 !important;
      }
      button[kind="secondary"]:hover {
        background: #1E1E1E !important;
        border-color: #404040 !important;
      }

      /* Tab Styling (Monolith Crisp White Active Indicator - No Blue) */
      button[data-baseweb="tab"] {
        color: #A1A1AA !important;
      }
      button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom-color: #FFFFFF !important;
      }
      div[data-baseweb="tab-highlight"] {
        background-color: #FFFFFF !important;
      }
      div[data-baseweb="tab-border"] {
        background-color: #262626 !important;
      }

      /* Sliders (Monolith White Accent - No Blue) */
      div[data-baseweb="slider"] div[role="slider"] {
        background-color: #FFFFFF !important;
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.4) !important;
      }
      div[data-baseweb="slider"] div[data-testid="stTickBar"] + div,
      div[data-baseweb="slider"] > div > div:nth-child(1) {
        background: #FFFFFF !important;
      }
      div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
      }

      /* Multiselect Tag Pill Styling (White Pill with High-Contrast Pitch Black Text) */
      .stMultiSelect [data-tag],
      [data-testid="stMultiSelect"] [data-tag],
      [data-testid="stMultiSelectTagsContainer"] [data-tag],
      span[data-tag],
      div[data-tag],
      span.e1kig3hy3,
      .e1kig3hy3,
      span[data-baseweb="tag"],
      div[data-baseweb="tag"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        border-radius: 6px !important;
        color: #000000 !important;
      }
      .stMultiSelect [data-tag] *,
      [data-testid="stMultiSelect"] [data-tag] *,
      [data-testid="stMultiSelectTagsContainer"] [data-tag] *,
      span[data-tag] *,
      div[data-tag] *,
      .e1kig3hy3 *,
      .e1kig3hy4,
      span[data-baseweb="tag"] *,
      div[data-baseweb="tag"] * {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 700 !important;
      }
      .stMultiSelect [data-tag] button,
      [data-testid="stMultiSelect"] [data-tag] button,
      span[data-tag] button,
      div[data-tag] button {
        color: #000000 !important;
        opacity: 0.8 !important;
      }
      .stMultiSelect [data-tag] button:hover,
      [data-testid="stMultiSelect"] [data-tag] button:hover,
      span[data-tag] button:hover,
      div[data-tag] button:hover {
        opacity: 1 !important;
      }
      .stMultiSelect [data-tag] svg,
      [data-testid="stMultiSelect"] [data-tag] svg,
      span[data-tag] svg,
      div[data-tag] svg,
      span[data-baseweb="tag"] svg,
      div[data-baseweb="tag"] svg {
        color: #000000 !important;
        fill: #000000 !important;
        stroke: #000000 !important;
      }
      .stMultiSelect [data-tag] svg path,
      [data-testid="stMultiSelect"] [data-tag] svg path,
      span[data-tag] svg path,
      div[data-tag] svg path {
        stroke: #000000 !important;
      }

      /* Multiselect Dropdown Menu (Clean Dark Obsidian) */
      div[data-testid="stMultiSelectDropdown"] {
        background-color: #0D0D0D !important;
        border: 1px solid #262626 !important;
        border-radius: 8px !important;
      }
      div[data-testid="stMultiSelectDropdown"] [role="option"] {
        color: #F4F4F5 !important;
      }
      div[data-testid="stMultiSelectDropdown"] [role="option"]:hover,
      div[data-testid="stMultiSelectDropdown"] [data-hovered] {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
      }
    </style>
    """
