"""
config.py — Central configuration for WC26 Equity Terminal
"""
import os

# ── Big Balls Data API ────────────────────────────────────────────────────────
# Free tier: 1,000 requests/day — no credit card
# Get your key at: https://bigballsdata.com/signup
# Replace the value below with your key, OR set env var BBS_API_KEY
BBS_API_KEY = os.environ.get("BBS_API_KEY", "YOUR_BBS_KEY_HERE")

# ── football-data.org (backup, for schedule only if needed) ───────────────────
FOOTBALL_DATA_API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY", "53566dc749cc466a91d0d2fceef2542c")
FOOTBALL_DATA_BASE    = "https://api.football-data.org/v4"
WORLD_CUP_ID          = int(os.environ.get("WORLD_CUP_ID", "2000"))

# ── Scheduler ─────────────────────────────────────────────────────────────────
# Poll every 5 minutes — well within free tier limits
MATCH_POLL_INTERVAL = int(os.environ.get("MATCH_POLL_INTERVAL", "300"))

# ── App ───────────────────────────────────────────────────────────────────────
APP_TITLE        = "WC26 Equity Terminal"
STARTING_CASH    = 50_000.0        # $50,000 per user
MIN_SHARES       = 0.01
TOURNAMENT_START = "2026-06-11"

# ── Match rating → price delta ────────────────────────────────────────────────
RATING_THRESHOLDS = [
    (8.5, +4.0),   # Outstanding
    (7.5, +2.0),   # Good
    (6.5,  0.0),   # Average
    (5.0, -1.0),   # Below par
    (0.0, -3.0),   # Poor
]

# ── Design palette ────────────────────────────────────────────────────────────
COLOR_BG         = "#0B0E1A"
COLOR_BG2        = "#0E122A"
COLOR_RED        = "#E61D25"
COLOR_GOLD       = "#C9A84C"
COLOR_GREEN      = "#2ECC71"
COLOR_BORDER     = "#1C2340"
COLOR_TEXT_DIM   = "#5A6080"
