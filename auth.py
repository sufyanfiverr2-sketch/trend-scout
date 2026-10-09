"""Authentication and user management for TrendScout.
Stores user credentials securely using PBKDF2-HMAC-SHA256 with per-user salt.
Backed by SQLite in data/trendscout.db.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import re
import secrets
import sqlite3
import uuid
from pathlib import Path
from typing import Optional, Tuple

DB_PATH = Path(__file__).parent / "data" / "trendscout.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database tables with indexes."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT,
                society_name TEXT,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_ideas (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                title TEXT,
                data_json TEXT NOT NULL,
                saved_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_saved_ideas_user ON saved_ideas(user_id)")
        conn.commit()


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()


def signup_user(
    username: str,
    password: str,
    display_name: str = "",
    society_name: str = "",
) -> Tuple[bool, str, Optional[dict]]:
    """Register a new user account. Returns (success, message, user_dict)."""
    init_db()
    uname = (username or "").strip().lower()
    if not uname:
        return False, "Username is required.", None
    if len(uname) < 3:
        return False, "Username must be at least 3 characters long.", None
    if not re.match(r"^[a-zA-Z0-9_.-]+$", uname):
        return (
            False,
            "Username can only contain letters, numbers, underscores, and hyphens.",
            None,
        )

    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    salt = secrets.token_hex(16)
    pw_hash = _hash_password(password, salt)
    user_id = uuid.uuid4().hex[:12]
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    display = (display_name or "").strip() or uname
    society = (society_name or "").strip()

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (id, username, display_name, society_name, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, uname, display, society, pw_hash, salt, now),
            )
            conn.commit()
        user_info = {
            "id": user_id,
            "username": uname,
            "display_name": display,
            "society_name": society,
        }
        return True, "Account created successfully! Welcome to TrendScout.", user_info
    except sqlite3.IntegrityError:
        return False, f"Username '@{uname}' is already taken. Please choose another.", None
    except Exception as e:
        return False, f"Registration error: {e}", None


def login_user(username: str, password: str) -> Tuple[bool, str, Optional[dict]]:
    """Authenticate an existing user. Returns (success, message, user_dict)."""
    init_db()
    uname = (username or "").strip().lower()
    if not uname or not password:
        return False, "Please enter both username and password.", None

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (uname,)
        ).fetchone()

    if not row:
        return False, "Account not found. Please check your username or sign up.", None

    stored_hash = row["password_hash"]
    salt = row["salt"]
    computed_hash = _hash_password(password, salt)

    if not hmac.compare_digest(stored_hash, computed_hash):
        return False, "Incorrect password. Please try again.", None

    user_info = {
        "id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"] or row["username"],
        "society_name": row["society_name"] or "",
    }
    return True, f"Welcome back, @{user_info['username']}!", user_info


def get_user_by_id(user_id: str) -> Optional[dict]:
    init_db()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row:
        return {
            "id": row["id"],
            "username": row["username"],
            "display_name": row["display_name"] or row["username"],
            "society_name": row["society_name"] or "",
        }
    return None
