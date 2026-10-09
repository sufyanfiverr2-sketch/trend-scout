"""Generates a high-definition 38-second walkthrough demo video (1280x720 @ 30fps)
showcasing TrendScout Studio:
1. Intro & Branding
2. Multi-User Sign Up & Login (PBKDF2 Hashing)
3. Trend Radar (Live Cultural Signals & Video Links)
4. Reel Ideas (Shot-by-Shot Scripts & Save Idea)
5. Cross-Device Vault Sync (SQLite Per-User Persistence)
6. Outro & GitHub Link
"""

import math
import os
import shutil
import sys
from pathlib import Path
import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1280
HEIGHT = 720
FPS = 30
DURATION_SEC = 38
TOTAL_FRAMES = FPS * DURATION_SEC

# Fonts
FONT_BOLD_PATH = "C:\\Windows\\Fonts\\segoeuib.ttf"
FONT_REG_PATH = "C:\\Windows\\Fonts\\segoeui.ttf"
FONT_CODE_PATH = "C:\\Windows\\Fonts\\consola.ttf"

def get_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

font_title = get_font(FONT_BOLD_PATH, 42)
font_h2 = get_font(FONT_BOLD_PATH, 28)
font_h3 = get_font(FONT_BOLD_PATH, 22)
font_body = get_font(FONT_REG_PATH, 19)
font_body_b = get_font(FONT_BOLD_PATH, 19)
font_small = get_font(FONT_REG_PATH, 15)
font_code = get_font(FONT_CODE_PATH, 16)
font_mono = get_font(FONT_CODE_PATH, 13)

# Colors (Monolith VIP Palette)
BG_DARK = (10, 10, 10)
BG_CARD = (18, 18, 18)
BORDER_CARD = (38, 38, 42)
TEXT_WHITE = (255, 255, 255)
TEXT_MUTED = (161, 161, 170)
TEXT_DIM = (113, 113, 122)
ACCENT_GREEN = (52, 211, 153)
ACCENT_BLUE = (96, 165, 250)
ACCENT_PURPLE = (192, 132, 252)
ACCENT_YELLOW = (250, 204, 21)

def draw_header_nav(draw, active_step: int, t_progress: float):
    # Top bar
    draw.rectangle([0, 0, WIDTH, 54], fill=(13, 13, 13))
    draw.line([0, 54, WIDTH, 54], fill=(28, 28, 28), width=1)
    
    # Logo & title
    draw.rectangle([24, 14, 52, 42], fill=(26, 26, 26), outline=(60, 60, 60), width=1)
    # triangle play
    draw.polygon([(34, 20), (45, 28), (34, 36)], fill=(255, 255, 255))
    draw.text((62, 15), "TrendScout Studio", font=font_h3, fill=TEXT_WHITE)
    draw.text((250, 19), "|", font=font_body, fill=TEXT_DIM)
    draw.text((265, 20), "University Reels Intelligence", font=font_small, fill=TEXT_MUTED)

    # Step badges
    steps = ["1. Register", "2. Trends", "3. Scripts", "4. Device Sync"]
    x = 760
    for idx, name in enumerate(steps):
        is_active = (idx == active_step)
        bg = (255, 255, 255) if is_active else (22, 22, 22)
        fg = (0, 0, 0) if is_active else (140, 140, 140)
        border = (255, 255, 255) if is_active else (40, 40, 40)
        
        draw.rounded_rectangle([x, 14, x + 115, 42], radius=6, fill=bg, outline=border, width=1)
        draw.text((x + 12, 19), name, font=font_small, fill=fg)
        x += 125

def draw_bottom_bar(draw, frame_idx: int):
    # Bottom timeline progress bar
    draw.rectangle([0, HEIGHT - 28, WIDTH, HEIGHT], fill=(8, 8, 8))
    draw.line([0, HEIGHT - 28, WIDTH, HEIGHT - 28], fill=(24, 24, 24), width=1)
    
    sec = frame_idx / FPS
    total_sec = DURATION_SEC
    pct = frame_idx / TOTAL_FRAMES
    
    # Progress fill
    draw.rectangle([0, HEIGHT - 4, int(WIDTH * pct), HEIGHT], fill=(255, 255, 255))
    
    time_str = f"{int(sec)//60:02d}:{int(sec)%60:02d} / {int(total_sec)//60:02d}:{int(total_sec)%60:02d}"
    draw.text((20, HEIGHT - 23), f"DEMO WALKTHROUGH · {time_str}", font=font_mono, fill=TEXT_MUTED)
    draw.text((WIDTH - 380, HEIGHT - 23), "Pitch Black Monolith Edition · SQLite Sync Enabled", font=font_mono, fill=TEXT_DIM)

def draw_sidebar(draw, user_logged: bool, society_name: str, username: str):
    # Left sidebar mockup
    draw.rectangle([0, 55, 280, HEIGHT - 28], fill=(12, 12, 12))
    draw.line([280, 55, 280, HEIGHT - 28], fill=(28, 28, 28), width=1)
    
    y = 75
    draw.text((20, y), "Society Profile", font=font_body_b, fill=TEXT_WHITE)
    y += 35
    
    # User status box
    if user_logged:
        draw.rounded_rectangle([18, y, 262, y + 62], radius=8, fill=(20, 20, 22), outline=(50, 50, 55), width=1)
        draw.text((28, y + 8), f"👤 @{username}", font=font_body_b, fill=TEXT_WHITE)
        draw.text((28, y + 33), f"🏛️ {society_name}", font=font_small, fill=ACCENT_GREEN)
        y += 75
    else:
        draw.rounded_rectangle([18, y, 262, y + 54], radius=8, fill=(18, 18, 18), outline=(40, 40, 40), width=1)
        draw.text((28, y + 10), "👀 Browsing as Guest", font=font_small, fill=TEXT_MUTED)
        draw.text((28, y + 30), "Login required to sync", font=font_mono, fill=TEXT_DIM)
        y += 66

    # Form fields
    fields = [
        ("Society name", society_name),
        ("Focus / Niche", "General / Fun / Memes"),
        ("Country / region", "Pakistan"),
        ("Language", "English with Roman Urdu"),
    ]
    for lbl, val in fields:
        draw.text((20, y), lbl, font=font_small, fill=TEXT_MUTED)
        y += 22
        draw.rounded_rectangle([18, y, 262, y + 34], radius=6, fill=(18, 18, 18), outline=(36, 36, 36), width=1)
        draw.text((28, y + 8), val[:28], font=font_small, fill=TEXT_WHITE)
        y += 46

    # Tone pills (Our high-contrast tags!)
    draw.text((20, y), "Comedy & content tone", font=font_small, fill=TEXT_MUTED)
    y += 22
    draw.rounded_rectangle([18, y, 262, y + 74], radius=6, fill=(18, 18, 18), outline=(36, 36, 36), width=1)
    
    # Pill 1: White box with BOLD BLACK TEXT
    draw.rounded_rectangle([24, y + 6, 210, y + 32], radius=4, fill=(255, 255, 255))
    draw.text((32, y + 10), "Pure Comedy / Memes  ✕", font=font_mono, fill=(0, 0, 0))
    
    # Pill 2: White box with BOLD BLACK TEXT
    draw.rounded_rectangle([24, y + 38, 200, y + 64], radius=4, fill=(255, 255, 255))
    draw.text((32, y + 42), "Relatable student life ✕", font=font_mono, fill=(0, 0, 0))

def render_frame(frame_idx: int) -> Image.Image:
    im = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(im)
    t = frame_idx / FPS
    
    # -------------------------------------------------------------
    # SCENE 1: Intro Splash (0.0s - 5.0s, frames 0-150)
    # -------------------------------------------------------------
    if frame_idx < 150:
        fade = min(1.0, t / 0.8)
        # Background subtle ambient glow
        draw.ellipse([WIDTH//2 - 350, HEIGHT//2 - 250, WIDTH//2 + 350, HEIGHT//2 + 250], fill=(16, 16, 20))
        
        # Central Logo
        box_y = 150
        draw.rounded_rectangle([WIDTH//2 - 44, box_y, WIDTH//2 + 44, box_y + 88], radius=18, fill=(18, 18, 18), outline=(50, 50, 50), width=2)
        draw.polygon([(WIDTH//2 - 14, box_y + 22), (WIDTH//2 + 20, box_y + 44), (WIDTH//2 - 14, box_y + 66)], fill=(255, 255, 255))
        
        # Title
        draw.text((WIDTH//2 - 210, box_y + 115), "TrendScout Studio", font=font_title, fill=TEXT_WHITE)
        
        # Subtitles
        draw.text((WIDTH//2 - 340, box_y + 185), "AI Trend Discovery & Comedic Reel Script Engine for Societies", font=font_h3, fill=TEXT_MUTED)
        
        # Features pill list
        draw.rounded_rectangle([WIDTH//2 - 310, box_y + 245, WIDTH//2 + 310, box_y + 300], radius=12, fill=(16, 16, 16), outline=(38, 38, 38), width=1)
        feat_text = "🔑 User Auth & Signup  ·  ⭐ Multi-Device Sync  ·  🎬 Shot-by-Shot Scripts"
        draw.text((WIDTH//2 - 280, box_y + 262), feat_text, font=font_body_b, fill=ACCENT_GREEN)

        draw.text((WIDTH//2 - 160, HEIGHT - 70), "Starting System Walkthrough...", font=font_small, fill=TEXT_DIM)
        draw_bottom_bar(draw, frame_idx)
        return im

    # -------------------------------------------------------------
    # SCENE 2: Registration & Login Walkthrough (5.0s - 13.0s, frames 150-390)
    # -------------------------------------------------------------
    elif frame_idx < 390:
        draw_header_nav(draw, active_step=0, t_progress=(frame_idx - 150) / 240)
        draw_sidebar(draw, user_logged=(frame_idx > 300), society_name="Youth & Events Society", username="sufyan")
        
        # Main area
        main_x = 310
        draw.text((main_x, 75), "User Authentication & Sign Up Portal", font=font_h2, fill=TEXT_WHITE)
        draw.text((main_x, 112), "Built with PBKDF2-HMAC-SHA256 encryption. Ideas persist across all devices.", font=font_body, fill=TEXT_MUTED)
        
        # Centered Auth Card Mockup
        card_x = main_x + 90
        card_y = 155
        card_w = 580
        card_h = 470
        draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=12, fill=(15, 15, 15), outline=(38, 38, 42), width=1)
        
        # Tab switch animation
        # Tab headers
        draw.rounded_rectangle([card_x + 20, card_y + 20, card_x + 280, card_y + 60], radius=8, fill=(255, 255, 255), outline=(255, 255, 255))
        draw.text((card_x + 85, card_y + 28), "✨ Create Account", font=font_body_b, fill=(0, 0, 0))
        
        draw.rounded_rectangle([card_x + 295, card_y + 20, card_x + 555, card_y + 60], radius=8, fill=(20, 20, 20), outline=(40, 40, 40))
        draw.text((card_x + 380, card_y + 28), "🔑 Sign In", font=font_body, fill=TEXT_MUTED)
        
        # Form simulated inputs typing
        fy = card_y + 80
        # Field 1: Full name
        draw.text((card_x + 25, fy), "Full Name", font=font_small, fill=TEXT_MUTED)
        draw.rounded_rectangle([card_x + 25, fy + 22, card_x + 555, fy + 58], radius=6, fill=(22, 22, 22), outline=(50, 50, 50))
        name_typed = "Muhammad Sufyan" if frame_idx > 180 else "Muhamm..."
        draw.text((card_x + 38, fy + 30), name_typed, font=font_body, fill=TEXT_WHITE)
        fy += 70

        # Field 2: Society Name
        draw.text((card_x + 25, fy), "Society / Club Name", font=font_small, fill=TEXT_MUTED)
        draw.rounded_rectangle([card_x + 25, fy + 22, card_x + 555, fy + 58], radius=6, fill=(22, 22, 22), outline=(50, 50, 50))
        soc_typed = "Youth & Events Society" if frame_idx > 210 else "Youth &..."
        draw.text((card_x + 38, fy + 30), soc_typed, font=font_body, fill=TEXT_WHITE)
        fy += 70

        # Field 3: Username
        draw.text((card_x + 25, fy), "Choose Username", font=font_small, fill=TEXT_MUTED)
        draw.rounded_rectangle([card_x + 25, fy + 22, card_x + 555, fy + 58], radius=6, fill=(22, 22, 22), outline=(50, 50, 50))
        user_typed = "sufyan" if frame_idx > 240 else "sufy..."
        draw.text((card_x + 38, fy + 30), user_typed, font=font_body, fill=TEXT_WHITE)
        fy += 70

        # Field 4: Password
        draw.text((card_x + 25, fy), "Password", font=font_small, fill=TEXT_MUTED)
        draw.rounded_rectangle([card_x + 25, fy + 22, card_x + 555, fy + 58], radius=6, fill=(22, 22, 22), outline=(50, 50, 50))
        pw_typed = "••••••••••••" if frame_idx > 270 else "••••••"
        draw.text((card_x + 38, fy + 30), pw_typed, font=font_body, fill=TEXT_WHITE)
        fy += 75

        # Button
        btn_bg = (255, 255, 255) if frame_idx <= 300 else (220, 252, 231)
        btn_text = "Create Account & Sign In ➔" if frame_idx <= 300 else "✓ Account Created! Logging in..."
        draw.rounded_rectangle([card_x + 25, fy, card_x + 555, fy + 45], radius=6, fill=btn_bg)
        draw.text((card_x + 160, fy + 11), btn_text, font=font_body_b, fill=(0, 0, 0))

        # Success toast message
        if frame_idx > 300:
            toast_w = 420
            draw.rounded_rectangle([main_x + 180, card_y + 120, main_x + 180 + toast_w, card_y + 185], radius=10, fill=(18, 32, 22), outline=ACCENT_GREEN, width=2)
            draw.text((main_x + 205, card_y + 135), "✅ Welcome @sufyan! Session initialized.", font=font_body_b, fill=TEXT_WHITE)
            draw.text((main_x + 205, card_y + 160), "SQLite vault bound to your account.", font=font_small, fill=TEXT_MUTED)

        draw_bottom_bar(draw, frame_idx)
        return im

    # -------------------------------------------------------------
    # SCENE 3: Trend Radar (13.0s - 21.0s, frames 390-630)
    # -------------------------------------------------------------
    elif frame_idx < 630:
        draw_header_nav(draw, active_step=1, t_progress=(frame_idx - 390) / 240)
        draw_sidebar(draw, user_logged=True, society_name="Youth & Events Society", username="sufyan")
        
        main_x = 310
        # Tab bar simulated
        tabs = ["🔥 Trend Radar", "🎬 Reel Ideas", "📣 Campaign Planner", "⭐ Saved", "⚙️ Settings"]
        tx = main_x
        for i, tab in enumerate(tabs):
            active = (i == 0)
            fg = TEXT_WHITE if active else TEXT_DIM
            draw.text((tx, 72), tab, font=font_body_b if active else font_body, fill=fg)
            if active:
                draw.line([tx, 98, tx + 125, 98], fill=TEXT_WHITE, width=2)
            tx += 170

        draw.line([main_x, 99, WIDTH - 40, 99], fill=(28, 28, 28), width=1)
        
        y = 120
        draw.text((main_x, y), "What's making people laugh right now?", font=font_h2, fill=TEXT_WHITE)
        draw.text((main_x, y + 36), "Pulls trending comedic formats, viral audios & memes without API costs.", font=font_body, fill=TEXT_MUTED)
        
        # Live badge
        draw.rounded_rectangle([WIDTH - 360, y + 6, WIDTH - 40, y + 38], radius=6, fill=(18, 28, 18), outline=ACCENT_GREEN)
        draw.text((WIDTH - 345, y + 12), "⚡ Live Signals: Google Trends PK & Reddit", font=font_mono, fill=ACCENT_GREEN)
        
        y += 85
        # Trend Card 1
        card_w = WIDTH - main_x - 40
        draw.rounded_rectangle([main_x, y, main_x + card_w, y + 180], radius=10, fill=(16, 16, 16), outline=BORDER_CARD, width=1)
        
        # Badges
        draw.rounded_rectangle([main_x + 20, y + 16, main_x + 130, y + 40], radius=12, fill=(30, 30, 30))
        draw.text((main_x + 30, y + 20), "🔥 Rising Trend", font=font_mono, fill=ACCENT_YELLOW)
        draw.rounded_rectangle([main_x + 140, y + 16, main_x + 220, y + 40], radius=12, fill=(30, 30, 30))
        draw.text((main_x + 152, y + 20), "🇵🇰 Pakistan", font=font_mono, fill=TEXT_MUTED)
        
        # Title
        draw.text((main_x + 20, y + 50), "Friday 'Black Kurta' Reality Check", font=font_h3, fill=TEXT_WHITE)
        desc = "Roasts the 'main character syndrome' when every boy dresses in black kurta for Jummah and campus."
        draw.text((main_x + 20, y + 84), desc, font=font_body, fill=TEXT_MUTED)
        
        # Hook box
        draw.rounded_rectangle([main_x + 20, y + 115, main_x + card_w - 200, y + 160], radius=6, fill=(24, 24, 26), outline=(60, 60, 60))
        draw.text((main_x + 32, y + 126), "Hook: \"POV: You wore a black kurta thinking you're the hero...\"", font=font_code, fill=TEXT_WHITE)
        
        # Watch button
        draw.rounded_rectangle([main_x + card_w - 180, y + 115, main_x + card_w - 20, y + 160], radius=6, fill=(255, 255, 255))
        draw.text((main_x + card_w - 165, y + 126), "▶ Watch Video", font=font_body_b, fill=(0, 0, 0))

        y += 200
        # Trend Card 2
        draw.rounded_rectangle([main_x, y, main_x + card_w, y + 170], radius=10, fill=(16, 16, 16), outline=BORDER_CARD, width=1)
        draw.rounded_rectangle([main_x + 20, y + 16, main_x + 150, y + 40], radius=12, fill=(30, 30, 30))
        draw.text((main_x + 30, y + 20), "📈 Global Viral POV", font=font_mono, fill=ACCENT_BLUE)
        draw.text((main_x + 20, y + 50), "The Dramatic 'Reporting Live' Reporter", font=font_h3, fill=TEXT_WHITE)
        desc2 = "Treats mundane student struggles like serious breaking news coverage."
        draw.text((main_x + 20, y + 84), desc2, font=font_body, fill=TEXT_MUTED)
        draw.rounded_rectangle([main_x + 20, y + 115, main_x + card_w - 20, y + 155], radius=6, fill=(22, 22, 22))
        draw.text((main_x + 30, y + 124), "1-Click Direct Instagram & Shorts Search Link embedded", font=font_small, fill=TEXT_MUTED)

        draw_bottom_bar(draw, frame_idx)
        return im

    # -------------------------------------------------------------
    # SCENE 4: Reel Ideas & Save Action (21.0s - 29.0s, frames 630-870)
    # -------------------------------------------------------------
    elif frame_idx < 870:
        draw_header_nav(draw, active_step=2, t_progress=(frame_idx - 630) / 240)
        draw_sidebar(draw, user_logged=True, society_name="Youth & Events Society", username="sufyan")
        
        main_x = 310
        # Tab bar
        tabs = ["🔥 Trend Radar", "🎬 Reel Ideas", "📣 Campaign Planner", "⭐ Saved", "⚙️ Settings"]
        tx = main_x
        for i, tab in enumerate(tabs):
            active = (i == 1)
            fg = TEXT_WHITE if active else TEXT_DIM
            draw.text((tx, 72), tab, font=font_body_b if active else font_body, fill=fg)
            if active:
                draw.line([tx, 98, tx + 115, 98], fill=TEXT_WHITE, width=2)
            tx += 170
        draw.line([main_x, 99, WIDTH - 40, 99], fill=(28, 28, 28), width=1)
        
        y = 115
        draw.text((main_x, y), "Ready-to-Film Comedic Reel Scripts", font=font_h2, fill=TEXT_WHITE)
        draw.text((main_x, y + 34), "Complete shot-by-shot lists, spoken dialogue & captions ready for campus filming.", font=font_body, fill=TEXT_MUTED)
        
        y += 75
        card_w = WIDTH - main_x - 40
        draw.rounded_rectangle([main_x, y, main_x + card_w, y + 430], radius=10, fill=(16, 16, 16), outline=BORDER_CARD, width=1)
        
        # Script header
        draw.text((main_x + 24, y + 18), "🎬 The 8am Lecture Ghost Town Report", font=font_h3, fill=TEXT_WHITE)
        draw.text((main_x + card_w - 210, y + 20), "Virality Rating: 9.6 / 10 🔥", font=font_body_b, fill=ACCENT_YELLOW)
        
        # Concept quote
        draw.rounded_rectangle([main_x + 24, y + 54, main_x + card_w - 24, y + 96], radius=6, fill=(24, 24, 26), outline=(48, 48, 52))
        draw.text((main_x + 36, y + 64), "Concept: Student holds rolled up paper like a news mic in an empty lecture hall.", font=font_small, fill=TEXT_WHITE)
        
        # Shot list table mockup
        ty = y + 110
        draw.rectangle([main_x + 24, ty, main_x + card_w - 24, ty + 30], fill=(26, 26, 30))
        draw.text((main_x + 36, ty + 7), "Time", font=font_mono, fill=TEXT_MUTED)
        draw.text((main_x + 110, ty + 7), "What to Film & Expressions", font=font_mono, fill=TEXT_MUTED)
        draw.text((main_x + 460, ty + 7), "Spoken Dialogue / Punchline", font=font_mono, fill=TEXT_MUTED)
        
        rows = [
            ("0-3s", "Dramatic serious reporter face, holding bottle like mic", "\"Reporting live from Hall 4...\""),
            ("3-7s", "Camera whips to empty chairs and sleeping professor", "\"Zero survivors. Entire section has perished.\""),
            ("7-12s", "One lone student enters canteen smelling samosas", "\"Wait... breaking update from the cafeteria.\""),
        ]
        ty += 30
        for r_time, r_vis, r_dia in rows:
            draw.rectangle([main_x + 24, ty, main_x + card_w - 24, ty + 36], fill=(18, 18, 20))
            draw.line([main_x + 24, ty + 36, main_x + card_w - 24, ty + 36], fill=(30, 30, 34), width=1)
            draw.text((main_x + 36, ty + 9), r_time, font=font_mono, fill=ACCENT_BLUE)
            draw.text((main_x + 110, ty + 9), r_vis[:45], font=font_small, fill=TEXT_WHITE)
            draw.text((main_x + 460, ty + 9), r_dia, font=font_small, fill=ACCENT_GREEN)
            ty += 36

        # Meta tags
        ty += 15
        draw.text((main_x + 24, ty), "🎵 Audio: Dramatic News Intro Remix", font=font_small, fill=TEXT_MUTED)
        draw.text((main_x + 360, ty), "🕒 Best Time: 6:30 PM PKT", font=font_small, fill=TEXT_MUTED)
        draw.text((main_x + 620, ty), "🧰 Props: Phone + Samosa", font=font_small, fill=TEXT_MUTED)

        # Star save button
        ty += 35
        save_btn_w = 170
        is_saved = (frame_idx > 720)
        btn_col = ACCENT_GREEN if is_saved else (255, 255, 255)
        btn_lbl = "✓ Saved to Vault" if is_saved else "⭐ Save Idea"
        
        draw.rounded_rectangle([main_x + 24, ty, main_x + 24 + save_btn_w, ty + 42], radius=6, fill=btn_col)
        draw.text((main_x + 44, ty + 10), btn_lbl, font=font_body_b, fill=(0, 0, 0))

        # Floating toast notification
        if is_saved:
            toast_x = WIDTH - 460
            toast_y = 120
            draw.rounded_rectangle([toast_x, toast_y, toast_x + 420, toast_y + 55], radius=8, fill=(20, 36, 24), outline=ACCENT_GREEN, width=2)
            draw.text((toast_x + 20, toast_y + 16), "⭐ Saved to @sufyan! Synced across devices.", font=font_body_b, fill=TEXT_WHITE)

        draw_bottom_bar(draw, frame_idx)
        return im

    # -------------------------------------------------------------
    # SCENE 5: Cross-Device Sync Demo (29.0s - 35.0s, frames 870-1050)
    # -------------------------------------------------------------
    elif frame_idx < 1050:
        draw_header_nav(draw, active_step=3, t_progress=(frame_idx - 870) / 180)
        
        main_x = 40
        card_w = WIDTH - 80
        
        draw.text((main_x, 72), "Multi-Device Sync Verification", font=font_h2, fill=TEXT_WHITE)
        draw.text((main_x, 108), "Access your saved scripts and ideas from any laptop, tablet or smartphone.", font=font_body, fill=TEXT_MUTED)
        
        # Dual Device Diagram
        dev_y = 150
        dev_w = (card_w - 60) // 2
        
        # Device 1: Workstation / Laptop
        draw.rounded_rectangle([main_x, dev_y, main_x + dev_w, dev_y + 450], radius=12, fill=(15, 15, 15), outline=BORDER_CARD, width=1)
        draw.rounded_rectangle([main_x + 20, dev_y + 16, main_x + 190, dev_y + 44], radius=6, fill=(26, 26, 26))
        draw.text((main_x + 30, dev_y + 22), "💻 Laptop (Session 1)", font=font_mono, fill=TEXT_WHITE)
        draw.text((main_x + 210, dev_y + 22), "Status: Logged in as @sufyan", font=font_small, fill=ACCENT_GREEN)
        
        # Laptop Saved List
        ly = dev_y + 65
        draw.text((main_x + 20, ly), "Saved Items (SQLite DB):", font=font_body_b, fill=TEXT_MUTED)
        ly += 30
        
        items = [
            ("🎬 The 8am Lecture Ghost Town Report", "Saved just now · Reel Script"),
            ("😂 Friday 'Black Kurta' Reality Check", "Saved 5m ago · Viral Trend"),
            ("📣 Welcome Party Mega Campaign", "Saved yesterday · Full Playbook"),
        ]
        for ititle, isub in items:
            draw.rounded_rectangle([main_x + 20, ly, main_x + dev_w - 20, ly + 68], radius=8, fill=(22, 22, 24), outline=(42, 42, 46))
            draw.text((main_x + 34, ly + 12), ititle[:35], font=font_body_b, fill=TEXT_WHITE)
            draw.text((main_x + 34, ly + 38), isub, font=font_mono, fill=TEXT_MUTED)
            draw.text((main_x + dev_w - 70, ly + 22), "⬇️ Export", font=font_mono, fill=ACCENT_BLUE)
            ly += 80

        # Sync Arrow in Middle
        mid_x = main_x + dev_w + 10
        pulse = int(12 * math.sin(t * 8))
        draw.text((mid_x + 4, dev_y + 200 + pulse), "⚡ SYNC ➔", font=font_h3, fill=ACCENT_GREEN)

        # Device 2: Mobile / Smartphone
        dev2_x = main_x + dev_w + 60
        draw.rounded_rectangle([dev2_x, dev_y, dev2_x + dev_w, dev_y + 450], radius=12, fill=(15, 15, 15), outline=ACCENT_GREEN if frame_idx > 920 else BORDER_CARD, width=1)
        draw.rounded_rectangle([dev2_x + 20, dev_y + 16, dev2_x + 200, dev_y + 44], radius=6, fill=(26, 26, 26))
        draw.text((dev2_x + 30, dev_y + 22), "📱 Smartphone (Session 2)", font=font_mono, fill=TEXT_WHITE)
        draw.text((dev2_x + 220, dev_y + 22), "Logged in as @sufyan", font=font_small, fill=ACCENT_GREEN)

        # Mobile Saved List (Mirroring identical database state)
        my = dev_y + 65
        draw.text((dev2_x + 20, my), "Live Synchronized Vault:", font=font_body_b, fill=TEXT_MUTED)
        my += 30
        for ititle, isub in items:
            draw.rounded_rectangle([dev2_x + 20, my, dev2_x + dev_w - 20, my + 68], radius=8, fill=(22, 22, 24), outline=ACCENT_GREEN if frame_idx > 960 else (42, 42, 46))
            draw.text((dev2_x + 34, my + 12), ititle[:35], font=font_body_b, fill=TEXT_WHITE)
            draw.text((dev2_x + 34, my + 38), "✓ Synced to mobile", font=font_mono, fill=ACCENT_GREEN)
            draw.text((dev2_x + dev_w - 70, my + 22), "Copy 📋", font=font_mono, fill=TEXT_WHITE)
            my += 80

        draw_bottom_bar(draw, frame_idx)
        return im

    # -------------------------------------------------------------
    # SCENE 6: Outro (35.0s - 38.0s, frames 1050-1140)
    # -------------------------------------------------------------
    else:
        # Outro clean splash
        draw.rounded_rectangle([WIDTH//2 - 400, 120, WIDTH//2 + 400, 560], radius=16, fill=(14, 14, 14), outline=(40, 40, 40), width=1)
        
        draw.text((WIDTH//2 - 200, 160), "TrendScout Studio", font=font_title, fill=TEXT_WHITE)
        draw.text((WIDTH//2 - 240, 225), "Ready for University Society Content Teams", font=font_h2, fill=ACCENT_GREEN)
        
        lines = [
            "✓ Multi-User Authentication with PBKDF2 Encryption",
            "✓ Cross-Device SQLite Saved Ideas Persistence",
            "✓ Keyless Live Web Signals (Google Trends & Reddit)",
            "✓ 1-Click Video Format Visual Search Links",
            "✓ Full Script, Audio, Props & Caption Generator",
        ]
        ly = 285
        for line in lines:
            draw.text((WIDTH//2 - 260, ly), line, font=font_body, fill=TEXT_WHITE)
            ly += 36

        draw.rounded_rectangle([WIDTH//2 - 270, 480, WIDTH//2 + 270, 526], radius=8, fill=(255, 255, 255))
        draw.text((WIDTH//2 - 245, 492), "github.com/sufyanfiverr2-sketch/trend-scout", font=font_body_b, fill=(0, 0, 0))

        draw_bottom_bar(draw, frame_idx)
        return im

def main():
    out_path = Path("d:/projects/trend-scout/demo_walkthrough.mp4")
    artifact_dir = Path("C:/Users/ITRONIX/.gemini/antigravity/brain/e8c781ba-b259-4a0b-bcc6-702bef5cdd4a")
    artifact_path = artifact_dir / "demo_walkthrough.mp4"

    print(f"Generating {TOTAL_FRAMES} frames ({DURATION_SEC}s @ {FPS}fps) to {out_path}...")
    
    writer = imageio.get_writer(
        str(out_path),
        fps=FPS,
        codec="libx264",
        quality=8,
        macro_block_size=16,
        ffmpeg_params=["-pix_fmt", "yuv420p"]
    )

    for i in range(TOTAL_FRAMES):
        frame = render_frame(i)
        writer.append_data(np.array(frame))
        if i % 150 == 0:
            print(f"Rendered {i}/{TOTAL_FRAMES} frames ({i/TOTAL_FRAMES*100:.0f}%)...")

    writer.close()
    print("Video generation complete!")
    
    # Copy to artifact folder for viewing
    shutil.copy2(out_path, artifact_path)
    print(f"Copied demo video to artifact directory: {artifact_path}")
    print(f"File size: {out_path.stat().st_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
