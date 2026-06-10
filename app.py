"""
app.py — WC26 Synthetic Equity Terminal
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone
import time
import os

import database as db
import valuation as val
import api_client as api
import config

st.set_page_config(
    page_title="WC26 Equity Terminal",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()
if not api.is_running():
    api.start_scheduler()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Nunito:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0B0E1A;
    color: #C8D0E0;
}
.stApp { background-color: #0B0E1A; }

section[data-testid="stSidebar"] {
    background: #0E122A !important;
    border-right: 1px solid #1C2340;
}
section[data-testid="stSidebar"] * { color: #C8D0E0 !important; }
section[data-testid="stSidebar"] .stTextInput input {
    background: #141830 !important;
    border: 1px solid #1C2340 !important;
    color: #fff !important;
    border-radius: 4px !important;
}

[data-testid="stMetric"] {
    background: #0E122A;
    border: 1px solid #1C2340;
    border-radius: 6px;
    padding: 14px 16px;
}
[data-testid="stMetricLabel"] {
    color: #5A6080 !important;
    font-size: 0.68rem !important;
    font-family: 'Inter', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}
[data-testid="stMetricValue"] {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    color: #C9A84C !important;
    font-size: 1.3rem !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.82rem !important;
}

.stButton > button {
    background: #E61D25 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 0.5rem 1.5rem !important;
    transition: background 0.2s !important;
}
.stButton > button:hover { background: #FF2D35 !important; }
.btn-gold > button { background: #C9A84C !important; color: #0B0E1A !important; }
.btn-green > button { background: #1a8a40 !important; color: #fff !important; }
.btn-sell > button { background: #1C2340 !important; color: #E61D25 !important;
    border: 1px solid #E61D25 !important; }

.stSelectbox > div > div, .stNumberInput > div > div > input,
.stTextInput > div > div > input {
    background: #0E122A !important;
    border: 1px solid #1C2340 !important;
    border-radius: 4px !important;
    color: #C8D0E0 !important;
    font-family: 'Inter', sans-serif !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #0E122A;
    border-bottom: 2px solid #E61D25;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #5A6080;
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border-radius: 0;
    padding: 10px 22px;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}
.stTabs [aria-selected="true"] {
    color: #fff !important;
    background: #0B0E1A !important;
    border-bottom: 2px solid #E61D25 !important;
}

.stDataFrame { border: 1px solid #1C2340; border-radius: 6px; }
thead tr th {
    background: #0E122A !important;
    color: #5A6080 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.68rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
tbody tr { background: #0B0E1A !important; }
tbody tr:hover { background: #111530 !important; }

h1 {
    font-family: 'Bebas Neue', sans-serif !important;
    color: #fff !important;
    letter-spacing: 3px !important;
    font-size: 2.2rem !important;
    line-height: 1 !important;
}
h2 {
    font-family: 'Inter', sans-serif !important;
    color: #5A6080 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
    border-bottom: 1px solid #1C2340 !important;
    padding-bottom: 8px !important;
    margin-top: 24px !important;
}
h3 {
    font-family: 'Bebas Neue', sans-serif !important;
    color: #C9A84C !important;
    letter-spacing: 2px !important;
    font-size: 1.3rem !important;
}

hr { border: none; border-top: 1px solid #1C2340; margin: 16px 0; }

.num { font-family: 'Nunito', sans-serif !important; }
.gain { color: #2ECC71 !important; }
.loss { color: #E61D25 !important; }
.gold { color: #C9A84C !important; }
.dim  { color: #5A6080 !important; }

.wc-card {
    background: #0E122A;
    border: 1px solid #1C2340;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.wc-card-red { border-left: 3px solid #E61D25 !important; }
.wc-card-gold { border-left: 3px solid #C9A84C !important; }
.wc-card-green { border-left: 3px solid #2ECC71 !important; }
.wc-card-locked { background: #120A08; border: 1px solid #3A1810; }

.ticker-bar {
    background: #E61D25;
    padding: 7px 16px;
    font-family: 'Nunito', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
    overflow-x: auto;
    letter-spacing: 0.03em;
    display: flex;
    gap: 20px;
    align-items: center;
    border-radius: 0;
    color: #fff;
    margin-bottom: 20px;
}
.t-item { display: flex; gap: 5px; align-items: center; white-space: nowrap; }
.t-id { color: rgba(255,255,255,0.6); font-size: 0.72rem; }
.t-up { color: #fff; }
.t-dn { color: #FFB0B0; }
.t-lock { color: #FFD580; }
.t-sep { color: rgba(255,255,255,0.2); }

.live-dot { width:7px;height:7px;border-radius:50%;background:#E61D25;display:inline-block;margin-right:5px; }
.lock-badge { background:#1A0F00;color:#C9A84C;border:1px solid #C9A84C44;
    padding:2px 8px;border-radius:3px;font-size:0.72rem;font-weight:600; }
.rating-pill { display:inline-block;padding:2px 7px;border-radius:12px;
    font-family:'Nunito',sans-serif;font-size:0.75rem;font-weight:700; }
.r-out  { background:#0D2018;color:#2ECC71;border:1px solid #2ECC7144; }
.r-good { background:#0D1A10;color:#7BCF8A;border:1px solid #7BCF8A44; }
.r-avg  { background:#1A1A0D;color:#C9A84C;border:1px solid #C9A84C44; }
.r-poor { background:#1A0F00;color:#FF8C00;border:1px solid #FF8C0044; }
.r-bad  { background:#1A0808;color:#E61D25;border:1px solid #E61D2544; }

.flag { font-size:1.1rem; }
.success-box { background:#061A0C;border-left:3px solid #2ECC71;padding:10px 14px;
    border-radius:0 4px 4px 0;font-family:'Inter',sans-serif;font-size:0.82rem;color:#2ECC71;margin:8px 0; }
.error-box { background:#1A0608;border-left:3px solid #E61D25;padding:10px 14px;
    border-radius:0 4px 4px 0;font-family:'Inter',sans-serif;font-size:0.82rem;color:#E61D25;margin:8px 0; }
.lock-box  { background:#1A0F00;border-left:3px solid #C9A84C;padding:10px 14px;
    border-radius:0 4px 4px 0;font-family:'Inter',sans-serif;font-size:0.82rem;color:#C9A84C;margin:8px 0; }
.info-box  { background:#0D1020;border-left:3px solid #2A398D;padding:10px 14px;
    border-radius:0 4px 4px 0;font-family:'Inter',sans-serif;font-size:0.82rem;color:#8090C0;margin:8px 0; }

.page-eyebrow {
    font-family:'Inter',sans-serif;font-size:0.7rem;color:#3A4060;
    letter-spacing:0.15em;text-transform:uppercase;margin-top:-12px;margin-bottom:20px;
}

.podium-card { background:#0E122A;border:1px solid #1C2340;border-radius:8px;padding:16px;text-align:center; }
.podium-medal { font-size:2rem; }
.podium-name { font-family:'Inter',sans-serif;font-size:0.92rem;color:#C8D0E0;font-weight:600;margin-top:6px; }
.podium-roi  { font-family:'Nunito',sans-serif;font-size:1.4rem;font-weight:700;margin-top:4px; }
.podium-val  { font-family:'Nunito',sans-serif;font-size:0.8rem;color:#5A6080;margin-top:2px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmil(v):   return f"${v/1_000_000:,.1f}M"
def fprice(v): return f"${v:,.2f}"
def fpct(v):   return f"{v:+.2f}%"

def pct_html(v, text=None):
    t = text or fpct(v)
    c = "gain" if v>0 else ("loss" if v<0 else "dim")
    return f'<span class="{c} num">{t}</span>'

def chg_pct(p):
    prev = p.get("prev_price", p["ipo_price"])
    return ((p["live_price"]-prev)/prev*100) if prev>0 else 0.0

def ipo_chg(p):
    ipo = p.get("ipo_price",1)
    return ((p["live_price"]-ipo)/ipo*100) if ipo>0 else 0.0

def rating_html(r):
    if r is None: return '<span class="dim" style="font-size:0.75rem">—</span>'
    if r>=8.5: return f'<span class="rating-pill r-out">{r:.1f} ★</span>'
    if r>=7.5: return f'<span class="rating-pill r-good">{r:.1f}</span>'
    if r>=6.5: return f'<span class="rating-pill r-avg">{r:.1f}</span>'
    if r>=5.0: return f'<span class="rating-pill r-poor">{r:.1f}</span>'
    return f'<span class="rating-pill r-bad">{r:.1f}</span>'

def lock_html(team_code, locked):
    if team_code in locked:
        return ' <span class="lock-badge">🔒 LIVE</span>'
    return ''

api_ready = config.FOOTBALL_DATA_API_KEY != "YOUR_FREE_KEY_HERE"


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;'
        'letter-spacing:3px;color:#fff;padding:8px 0 4px 0;">'
        '<span style="color:#E61D25">WC</span>26 EQUITY TERMINAL</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div style="height:1px;background:#1C2340;margin-bottom:12px"></div>',
                unsafe_allow_html=True)

    if "username" not in st.session_state:
        st.session_state.username = ""

    uname = st.text_input("👤 Username", value=st.session_state.username,
                           placeholder="Pick a name to start…").strip()
    if uname and uname != st.session_state.username:
        st.session_state.username = uname
        db.get_or_create_user(uname)
        st.rerun()

    if st.session_state.username:
        user = db.get_or_create_user(st.session_state.username)
        holdings = db.get_holdings(st.session_state.username)
        hval = sum(h["shares"]*h["live_price"] for h in holdings)
        total = user["cash"] + hval
        roi   = ((total - config.STARTING_CASH) / config.STARTING_CASH) * 100

        st.markdown(
            f'<div style="background:#141830;border:1px solid #1C2340;border-radius:6px;'
            f'padding:12px;margin-bottom:12px;">'
            f'<div style="font-size:0.65rem;color:#3A4060;text-transform:uppercase;'
            f'letter-spacing:0.15em;margin-bottom:8px;">Manager Account</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-weight:600;'
            f'font-size:0.95rem;color:#fff;margin-bottom:10px;">{st.session_state.username}</div>'
            f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
            f'<span style="font-size:0.72rem;color:#5A6080">Cash</span>'
            f'<span style="font-family:\'Nunito\',sans-serif;font-size:0.78rem;'
            f'color:#C9A84C;font-weight:700">{fmil(user["cash"])}</span></div>'
            f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
            f'<span style="font-size:0.72rem;color:#5A6080">Portfolio</span>'
            f'<span style="font-family:\'Nunito\',sans-serif;font-size:0.78rem;'
            f'color:#C9A84C;font-weight:700">{fmil(total)}</span></div>'
            f'<div style="display:flex;justify-content:space-between;">'
            f'<span style="font-size:0.72rem;color:#5A6080">ROI</span>'
            f'<span style="font-family:\'Nunito\',sans-serif;font-size:0.78rem;font-weight:700;'
            f'color:{"#2ECC71" if roi>=0 else "#E61D25"}">{roi:+.3f}%</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="info-box">Enter a username to create your $700M account and start trading.</div>',
            unsafe_allow_html=True
        )

    live = db.get_live_matches()
    locked = db.get_locked_teams()
    if live:
        for m in live[:2]:
            st.markdown(
                f'<div style="background:#0A1A0A;border:1px solid #1A4A1A;border-radius:6px;'
                f'padding:8px 10px;margin-bottom:6px;font-size:0.75rem;">'
                f'<div style="color:#E61D25;font-weight:700;font-size:0.65rem;'
                f'letter-spacing:0.1em;margin-bottom:4px;">● LIVE</div>'
                f'<div style="color:#C8D0E0;font-weight:600;">'
                f'{m["home_team_code"]} '
                f'<span style="font-family:\'Nunito\',sans-serif;color:#C9A84C;font-weight:700;">'
                f'{m["home_score"] or 0}–{m["away_score"] or 0}</span>'
                f' {m["away_team_code"]}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown('<div style="height:1px;background:#1C2340;margin:8px 0"></div>', unsafe_allow_html=True)

    page = st.radio("Navigate", [
        "📖 How to Play",
        "🏦 Market Terminal", "📅 Match Schedule",
        "💼 My Portfolio", "⚡ Trade Desk",
        "🏆 Leaderboard", "🔧 Admin Panel"
    ], label_visibility="collapsed")

    st.markdown(
        f'<div style="font-size:0.65rem;color:#2A3050;font-family:\'Inter\',sans-serif;'
        f'line-height:1.9;margin-top:12px;padding-top:10px;border-top:1px solid #1C2340;">'
        f'SCHEDULER {"🟢" if api.is_running() else "🔴"} {"ON" if api.is_running() else "OFF"}<br>'
        f'API {"🟢 LIVE" if api_ready else "⚪ AWAITING KEY"}<br>'
        f'{len(db.get_all_players())} INSTRUMENTS<br>'
        f'{"🔒 "+str(len(locked))+" TEAMS LOCKED" if locked else "🔓 ALL UNLOCKED"}<br>'
        f'{datetime.now(timezone.utc).strftime("%d %b %Y %H:%M")} UTC</div>',
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — MARKET TERMINAL
# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 0 — HOW TO PLAY
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📖 How to Play":
    st.title("HOW TO PLAY")
    st.markdown(
        '<div class="page-eyebrow">WC26 Equity Terminal · Complete Guide · Share this with your friends</div>',
        unsafe_allow_html=True
    )

    # ── What is this ─────────────────────────────────────────────────────────
    st.markdown(
        '<div class="wc-card wc-card-red" style="padding:24px;margin-bottom:20px;">'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.6rem;'
        'letter-spacing:3px;color:#fff;margin-bottom:12px;">WHAT IS THIS?</div>'
        '<div style="font-size:0.92rem;color:#8090B0;line-height:1.8;">'
        'This is a synthetic stock market built around the 2026 FIFA World Cup. '
        'Every player in the tournament is a tradeable instrument with a share price. '
        'Prices go up when players perform well and down when they perform badly — '
        'based entirely on real match results, automatically fetched after each game. '
        'You start with <span style="color:#C9A84C;font-weight:700">$700,000,000</span> '
        'and compete against your friends to build the highest-value portfolio by the final on 19 July 2026.'
        '</div></div>',
        unsafe_allow_html=True
    )

    # ── Getting started ───────────────────────────────────────────────────────
    st.markdown("## Getting Started")
    col1, col2, col3 = st.columns(3)
    steps = [
        ("1", "#E61D25", "Pick a Username",
         "Type any name in the sidebar. Your $700M account is created instantly. "
         "Your username is permanent — pick something good."),
        ("2", "#C9A84C", "Browse the Market",
         "Go to Market Terminal to see all players with their IPO prices, positions, "
         "nations and price history. Search by name, team or ticker."),
        ("3", "#2ECC71", "Start Trading",
         "Go to Trade Desk, pick a player, choose BUY, enter a quantity and execute. "
         "You can trade any time except during a live match."),
    ]
    for col, (num, colour, title, desc) in zip([col1,col2,col3], steps):
        col.markdown(
            f'<div class="wc-card" style="border-top:3px solid {colour};padding:18px;height:180px;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2rem;color:{colour};line-height:1">{num}</div>'
            f'<div style="font-weight:600;color:#fff;font-size:0.9rem;margin:6px 0;">{title}</div>'
            f'<div style="font-size:0.8rem;color:#5A6080;line-height:1.6">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── How pricing works ─────────────────────────────────────────────────────
    st.markdown("## How Prices Move")
    st.markdown(
        '<div class="info-box" style="margin-bottom:16px;">Prices <b>only move after a real match finishes</b>. '
        'Nothing happens during the game. At full time, the app automatically fetches the result '
        'and applies all the rules below simultaneously.</div>',
        unsafe_allow_html=True
    )

    pr1, pr2, pr3, pr4 = st.columns(4)
    pricing_data = [
        ("⚽ Attackers", "#E61D25", [
            ("Goal scored",        "+5%"),
            ("Assist",             "+3%"),
            ("xG outperformed",    "+2%"),
            ("Key pass",           "+1%"),
            ("Penalty miss",       "−4%"),
            ("Big chance missed",  "−2%"),
        ]),
        ("🎯 Midfielders", "#C9A84C", [
            ("Pass accuracy >90%",   "+3%"),
            ("Progressive pass",     "+2%"),
            ("Interception",         "+1.5%"),
            ("Dispossessed",         "−2%"),
            ("Yellow card",          "−1%"),
            ("Red card",             "−5%"),
        ]),
        ("🧱 Defenders & GKs", "#2A398D", [
            ("Clean sheet",          "+5%"),
            ("Save (GK)",            "+1.5%"),
            ("Tackle won",           "+1%"),
            ("Goal conceded",        "−2%"),
            ("Own goal",             "−6%"),
            ("Error to goal",        "−5%"),
        ]),
        ("🏆 Team & Rating", "#7B68EE", [
            ("Team wins",            "+1%"),
            ("Team advances",        "+3%"),
            ("Team eliminated",      "−4%"),
            ("Rating 8.5+",          "+4%"),
            ("Rating 7.5–8.4",       "+2%"),
            ("Rating below 5.0",     "−3%"),
        ]),
    ]

    for col, (title, colour, rules) in zip([pr1,pr2,pr3,pr4], pricing_data):
        rows_html = "".join(
            f'<div style="display:flex;justify-content:space-between;padding:4px 0;'
            f'border-bottom:1px solid #1C2340;">'
            f'<span style="font-size:0.78rem;color:#8090B0">{rule}</span>'
            f'<span style="font-family:\'Nunito\',sans-serif;font-size:0.78rem;font-weight:700;'
            f'color:{"#2ECC71" if "+" in val else "#E61D25"}">{val}</span></div>'
            for rule, val in rules
        )
        col.markdown(
            f'<div class="wc-card" style="border-top:3px solid {colour};">'
            f'<div style="font-size:0.72rem;font-weight:600;color:{colour};'
            f'text-transform:uppercase;letter-spacing:0.12em;margin-bottom:10px;">{title}</div>'
            f'{rows_html}</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="wc-card" style="margin-top:4px;background:#0a0d1e;">'
        '<div style="font-size:0.72rem;color:#5A6080;text-transform:uppercase;'
        'letter-spacing:0.12em;margin-bottom:6px;">Important: How Changes Combine</div>'
        '<div style="font-size:0.82rem;color:#8090B0;line-height:1.7">'
        'All % changes <b style="color:#C9A84C">compound multiplicatively</b>, not additively. '
        'So if Mbappé scores twice (+5% twice), gets an assist (+3%), his team wins (+1%) '
        'and he gets a 9.2 rating (+4%), his final price change is roughly <b style="color:#2ECC71">+19%</b> — '
        'not just the sum. Big performances lead to big price moves.'
        '</div></div>',
        unsafe_allow_html=True
    )

    # ── Trading rules ─────────────────────────────────────────────────────────
    st.markdown("## Trading Rules")
    tr1, tr2 = st.columns(2)
    with tr1:
        st.markdown(
            '<div class="wc-card wc-card-gold">'
            '<div style="font-size:0.72rem;color:#C9A84C;text-transform:uppercase;'
            'letter-spacing:0.12em;margin-bottom:10px;">✅ You Can</div>'
            '<ul style="font-size:0.84rem;color:#8090B0;line-height:2;margin:0;padding-left:16px;">'
            '<li>Buy and sell any player at any time</li>'
            '<li>Trade fractional shares (e.g. 250.5 shares)</li>'
            '<li>Hold multiple players simultaneously</li>'
            '<li>Sell before a match if you think a player will underperform</li>'
            '<li>Buy after a match at the new price</li>'
            '<li>Check your friends\' portfolios on the Leaderboard</li>'
            '</ul></div>',
            unsafe_allow_html=True
        )
    with tr2:
        st.markdown(
            '<div class="wc-card wc-card-red">'
            '<div style="font-size:0.72rem;color:#E61D25;text-transform:uppercase;'
            'letter-spacing:0.12em;margin-bottom:10px;">🔒 You Cannot</div>'
            '<ul style="font-size:0.84rem;color:#8090B0;line-height:2;margin:0;padding-left:16px;">'
            '<li>Trade any player while their team is playing</li>'
            '<li>Sell shares you don\'t own (no short selling)</li>'
            '<li>Spend more cash than you have</li>'
            '<li>Change your username once set</li>'
            '<li>Trade after the tournament final on 19 July 2026</li>'
            '</ul></div>',
            unsafe_allow_html=True
        )

    # ── Tournament timeline ───────────────────────────────────────────────────
    st.markdown("## Tournament Timeline")
    stages = [
        ("11 Jun","Group Stage Begins","48 matches · 12 groups of 4 · Mexico vs South Africa opens","#E61D25"),
        ("27 Jun","Group Stage Ends","Top 2 from each group + 8 best 3rd-placed advance","#C9A84C"),
        ("30 Jun","Round of 32 Begins","Stage advance bonus: +3% for all players on qualifying teams","#C9A84C"),
        ("11 Jul","Quarter-Finals","Only 8 teams remain · Elimination hits -4% for all eliminated players","#7B68EE"),
        ("15 Jul","Semi-Finals","4 teams left · Biggest price swings of the tournament","#2A398D"),
        ("19 Jul","THE FINAL","MetLife Stadium, New Jersey · Champions crowned","#2ECC71"),
    ]
    for date, title, desc, colour in stages:
        st.markdown(
            f'<div style="display:flex;gap:16px;margin-bottom:8px;align-items:flex-start;">'
            f'<div style="min-width:56px;font-family:\'Bebas Neue\',sans-serif;font-size:0.95rem;'
            f'color:{colour};letter-spacing:1px;padding-top:2px;">{date}</div>'
            f'<div style="flex:1;background:#0E122A;border:1px solid #1C2340;border-left:3px solid {colour};'
            f'border-radius:0 6px 6px 0;padding:10px 14px;">'
            f'<div style="font-weight:600;color:#fff;font-size:0.88rem">{title}</div>'
            f'<div style="font-size:0.78rem;color:#5A6080;margin-top:3px">{desc}</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    # ── Strategy tips ─────────────────────────────────────────────────────────
    st.markdown("## Strategy Tips")
    tips = [
        ("🎯", "Buy Before Big Matches",
         "If Argentina play a weak team, buy Messi before kickoff. "
         "If he scores and Argentina win, you're looking at +9% or more in a single match."),
        ("📈", "Sell Into Rallies",
         "After a big price jump, consider taking profits. "
         "A player who scored in the group stage might not repeat in the next game."),
        ("🏆", "Target Stage Advancers",
         "When a strong team advances to the knockouts, every player on that team gets +3%. "
         "Hold a spread of players from teams likely to go deep in the tournament."),
        ("🧱", "Don't Ignore Defenders",
         "A goalkeeper with a clean sheet earns +5% — same as a striker scoring. "
         "A great defensive performance can be just as valuable as goals."),
        ("⚡", "React Fast After Results",
         "Prices update the moment a match finishes. "
         "If a player had a poor rating (below 5.0), their price drops -3% on top of other penalties. "
         "Be ready to buy the dip or sell before the next game."),
        ("🌍", "Diversify By Nation",
         "Don't put everything into one team. "
         "If a key player gets injured or their team gets eliminated, "
         "you want holdings in other nations to cushion the blow."),
    ]
    t1, t2 = st.columns(2)
    for i, (icon, title, desc) in enumerate(tips):
        col = t1 if i % 2 == 0 else t2
        col.markdown(
            f'<div class="wc-card" style="margin-bottom:10px;">'
            f'<div style="font-size:1.2rem;margin-bottom:6px">{icon}</div>'
            f'<div style="font-weight:600;color:#fff;font-size:0.88rem;margin-bottom:4px">{title}</div>'
            f'<div style="font-size:0.8rem;color:#5A6080;line-height:1.6">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── Leaderboard explained ─────────────────────────────────────────────────
    st.markdown("## The Leaderboard")
    st.markdown(
        '<div class="wc-card wc-card-gold">'
        '<div style="font-size:0.84rem;color:#8090B0;line-height:1.8;">'
        'The leaderboard ranks all managers by <b style="color:#C9A84C">ROI% (Return on Investment)</b> — '
        'how much your portfolio has grown from the $700M starting capital.<br><br>'
        '<b style="color:#fff">Total Portfolio Value</b> = Cash remaining + '
        'Market value of all your current holdings<br>'
        '<b style="color:#fff">ROI%</b> = (Total Value − $700M) ÷ $700M × 100<br><br>'
        'A manager who spends wisely and sells at the right time will outperform someone '
        'who just holds everything. The winner is whoever has the highest ROI% when the '
        'final whistle blows at MetLife Stadium on 19 July 2026.'
        '</div></div>',
        unsafe_allow_html=True
    )

    # ── Share section ─────────────────────────────────────────────────────────
    st.markdown("## Share With Friends")
    st.markdown(
        '<div class="wc-card" style="text-align:center;padding:28px;">'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.4rem;'
        'letter-spacing:3px;color:#C9A84C;margin-bottom:8px;">HOW TO INVITE FRIENDS</div>'
        '<div style="font-size:0.85rem;color:#8090B0;max-width:520px;margin:0 auto;line-height:1.8;">'
        'Send your friends the app link. They open it, pick a username, and they\'re in — '
        'their own $700M account, the same shared market, and they appear on the leaderboard instantly. '
        'No signup, no download, no account needed. Just a name and they\'re playing.'
        '</div>'
        '<div style="margin-top:16px;font-size:0.78rem;color:#3A4060;">'
        'Deploy to Streamlit Cloud for a permanent shareable link — see the setup guide.'
        '</div></div>',
        unsafe_allow_html=True
    )


elif page == "🏦 Market Terminal":
    players = db.get_all_players()
    locked  = db.get_locked_teams()
    for p in players:
        p["chg"] = chg_pct(p)
        p["ipc"] = ipo_chg(p)

    st.title("MARKET TERMINAL")
    st.markdown(
        f'<div class="page-eyebrow">FIFA World Cup 2026 · Post-Match Pricing · '
        f'{len(players)} Instruments · {datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")}</div>',
        unsafe_allow_html=True
    )

    # Ticker
    ticker_items = sorted(players, key=lambda x: abs(x["chg"]), reverse=True)[:20]
    ticker_html = '<div class="ticker-bar">'
    ticker_html += '<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;letter-spacing:2px;margin-right:8px;">LIVE PRICES</span>'
    ticker_html += '<span class="t-sep">|</span>'
    for p in ticker_items:
        if p["team_code"] in locked:
            css, arrow = "t-lock", "🔒"
        elif p["chg"] > 0:
            css, arrow = "t-up", "▲"
        elif p["chg"] < 0:
            css, arrow = "t-dn", "▼"
        else:
            css, arrow = "t-id", "—"
        ticker_html += (
            f'<span class="t-item"><span class="t-id">{p["flag"]} {p["id"]}</span>'
            f'<span class="{css}">${p["live_price"]:.2f} {arrow}{abs(p["chg"]):.2f}%</span></span>'
            f'<span class="t-sep">|</span>'
        )
    ticker_html += '</div>'
    st.markdown(ticker_html, unsafe_allow_html=True)

    # Summary metrics
    summary = val.get_market_summary()
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Market Cap", fmil(summary["market_cap"]))
    c2.metric("Advancing",  f'{summary["advancing"]} / {summary["total"]}',
              delta=f'+{summary["advancing"]}')
    c3.metric("Declining",  f'{summary["declining"]} / {summary["total"]}',
              delta=f'-{summary["declining"]}', delta_color="inverse")
    c4.metric("Locked Teams", f'{len(locked)}')
    c5.metric("Matches Played",
              str(len([m for m in db.get_all_matches() if m["status"]=="FINISHED"])))

    st.markdown("## Top Movers")
    cg, cl = st.columns(2)

    with cg:
        st.markdown(
            '<div style="font-size:0.7rem;color:#2ECC71;text-transform:uppercase;'
            'letter-spacing:0.15em;margin-bottom:10px;">📈 Top Gainers</div>',
            unsafe_allow_html=True
        )
        for p in summary["top_gainers"]:
            c = chg_pct(p)
            st.markdown(
                f'<div class="wc-card wc-card-green">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div><span class="flag">{p.get("flag","")}</span> '
                f'<b style="color:#fff;font-size:0.88rem">{p["id"]}</b> '
                f'<span style="color:#8090B0;font-size:0.82rem">{p["name"]}</span>'
                f'{lock_html(p["team_code"],locked)}</div>'
                f'<div style="text-align:right">{rating_html(p.get("last_rating"))}</div></div>'
                f'<div style="margin-top:6px;display:flex;justify-content:space-between;align-items:baseline;">'
                f'<span class="num gold" style="font-size:1.1rem;font-weight:700">${p["live_price"]:.2f}</span>'
                f'{pct_html(c)}</div></div>',
                unsafe_allow_html=True
            )

    with cl:
        st.markdown(
            '<div style="font-size:0.7rem;color:#E61D25;text-transform:uppercase;'
            'letter-spacing:0.15em;margin-bottom:10px;">📉 Top Losers</div>',
            unsafe_allow_html=True
        )
        for p in summary["top_losers"]:
            c = chg_pct(p)
            st.markdown(
                f'<div class="wc-card wc-card-red">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div><span class="flag">{p.get("flag","")}</span> '
                f'<b style="color:#fff;font-size:0.88rem">{p["id"]}</b> '
                f'<span style="color:#8090B0;font-size:0.82rem">{p["name"]}</span>'
                f'{lock_html(p["team_code"],locked)}</div>'
                f'<div style="text-align:right">{rating_html(p.get("last_rating"))}</div></div>'
                f'<div style="margin-top:6px;display:flex;justify-content:space-between;align-items:baseline;">'
                f'<span class="num gold" style="font-size:1.1rem;font-weight:700">${p["live_price"]:.2f}</span>'
                f'{pct_html(c)}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown("## Player Directory")
    fc1,fc2,fc3,fc4 = st.columns([2,1,1,1])
    with fc1: search  = st.text_input("🔍 Search player, team or ticker", placeholder="Messi, BRA, ARG…").lower()
    with fc2: pos_f   = st.selectbox("Position", ["ALL","ATT","MID","DEF","GK"])
    with fc3: sort_by = st.selectbox("Sort by", ["Live Price","% Change","vs IPO","Rating","Volume"])
    with fc4: sort_d  = st.selectbox("Order", ["↓ High→Low","↑ Low→High"])

    filtered = players.copy()
    if search:
        filtered = [p for p in filtered if
                    search in p["name"].lower() or search in p["team"].lower()
                    or search in p["id"].lower() or search in p["team_code"].lower()]
    if pos_f != "ALL":
        filtered = [p for p in filtered if p["pos"]==pos_f]

    sk = {"Live Price":"live_price","% Change":"chg","vs IPO":"ipc",
          "Rating":"last_rating","Volume":"volume"}[sort_by]
    filtered.sort(key=lambda x: (x.get(sk) or 0), reverse=(sort_d=="↓ High→Low"))

    rows = []
    for p in filtered:
        rows.append({
            "":        p.get("flag",""),
            "Ticker":  p["id"],
            "Player":  p["name"],
            "Pos":     p["pos"],
            "Nation":  p["team"],
            "🔒":      "🔒" if p["team_code"] in locked else "",
            "IPO $":   round(p["ipo_price"],2),
            "Live $":  round(p["live_price"],2),
            "Chg %":   round(p["chg"],3),
            "vs IPO":  round(p["ipc"],3),
            "Rating":  round(p["last_rating"],1) if p.get("last_rating") else None,
            "Vol":     p["volume"],
        })

    df = pd.DataFrame(rows)
    def _hl(row):
        c = row["Chg %"]
        if c>0:   return ["background-color:#051A0C"]*len(row)
        elif c<0: return ["background-color:#1A0508"]*len(row)
        return [""]*len(row)

    st.dataframe(
        df.style.apply(_hl, axis=1)
          .format({"IPO $":"${:.2f}","Live $":"${:.2f}",
                   "Chg %":"{:+.3f}%","vs IPO":"{:+.3f}%"}, na_rep="—"),
        use_container_width=True, height=480,
    )

    st.markdown("## Price Chart")
    opts = {f'{p["flag"]} {p["id"]} — {p["name"]}': p["id"] for p in players}
    sel  = st.selectbox("Select player", list(opts.keys()))
    sid  = opts[sel]
    sp   = next(p for p in players if p["id"]==sid)
    hist = db.get_price_history(sid, 300)

    if len(hist) > 1:
        hdf = pd.DataFrame(hist)
        hdf["ts"] = pd.to_datetime(hdf["ts"])
        lc  = "#2ECC71" if hdf["price"].iloc[-1] >= hdf["price"].iloc[0] else "#E61D25"
        fc_ = "rgba(46,204,113,0.07)" if lc=="#2ECC71" else "rgba(230,29,37,0.07)"
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hdf["ts"], y=hdf["price"], mode="lines+markers", name=sid,
            line=dict(color=lc, width=2), marker=dict(size=4, color=lc),
            fill="tozeroy", fillcolor=fc_,
            hovertemplate="<b>$%{y:.2f}</b><br>%{x}<extra></extra>",
        ))
        fig.add_hline(y=sp["ipo_price"], line_dash="dash", line_color="#2A398D",
                      annotation_text=f'IPO ${sp["ipo_price"]:.2f}',
                      annotation_font_color="#2A398D")
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0B0E1A", plot_bgcolor="#0E122A",
            font=dict(family="Inter", color="#5A6080", size=11),
            xaxis=dict(gridcolor="#1C2340"), yaxis=dict(gridcolor="#1C2340", tickprefix="$"),
            margin=dict(l=50,r=20,t=40,b=40), height=340,
            title=dict(text=f'{sp["flag"]} {sp["name"]} ({sid}) — Price History',
                       font=dict(color="#C9A84C", size=13, family="Bebas Neue")),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(
            '<div class="info-box">No price history yet. Prices will update automatically after the first World Cup match on 11 June 2026.</div>',
            unsafe_allow_html=True
        )

    st.markdown("## Indexed Comparison")
    cmp = st.multiselect("Compare 2–5 players (base = 100)", list(opts.keys()), default=list(opts.keys())[:3])
    if len(cmp) >= 2:
        colors = ["#2ECC71","#E61D25","#C9A84C","#7B68EE","#00BFFF"]
        fig2 = go.Figure()
        for i, label in enumerate(cmp[:5]):
            pid = opts[label]
            h2  = db.get_price_history(pid, 200)
            if len(h2)>1:
                df2 = pd.DataFrame(h2)
                df2["ts"] = pd.to_datetime(df2["ts"])
                df2["idx"] = (df2["price"]/df2["price"].iloc[0])*100
                fig2.add_trace(go.Scatter(x=df2["ts"],y=df2["idx"],mode="lines",
                    name=pid, line=dict(color=colors[i%5],width=2)))
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="#0B0E1A", plot_bgcolor="#0E122A",
            font=dict(family="Inter",color="#5A6080",size=11),
            xaxis=dict(gridcolor="#1C2340"), yaxis=dict(gridcolor="#1C2340",ticksuffix=" idx"),
            margin=dict(l=50,r=20,t=40,b=40), height=320,
            title=dict(text="Indexed Price Comparison",font=dict(color="#C9A84C",size=13,family="Bebas Neue")),
            legend=dict(bgcolor="#0E122A",bordercolor="#1C2340"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    if st.button("🔄 Refresh Market"):
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MATCH SCHEDULE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📅 Match Schedule":
    st.title("MATCH SCHEDULE")
    st.markdown(
        '<div class="page-eyebrow">FIFA World Cup 2026 · Trading locks at kickoff · '
        'Prices update at full time</div>', unsafe_allow_html=True
    )

    if not api_ready:
        st.markdown(
            '<div class="info-box">⚪ No API key configured yet. The match schedule will load automatically '
            'once you add your free football-data.org API key to config.py. '
            'The tournament begins 11 June 2026.</div>',
            unsafe_allow_html=True
        )

    matches = db.get_all_matches(104)
    live_m     = [m for m in matches if m["status"] in ("IN_PLAY","PAUSED")]
    upcoming_m = [m for m in matches if m["status"] in ("SCHEDULED","TIMED")]
    finished_m = [m for m in matches if m["status"] in ("FINISHED","AWARDED")]

    if live_m:
        st.markdown("## Live Now")
        for m in live_m:
            st.markdown(
                f'<div class="wc-card" style="background:#0A1A0A;border:1px solid #1A4A1A;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div style="display:flex;align-items:center;gap:14px;">'
                f'<span style="background:#E61D25;color:#fff;font-size:0.65rem;font-weight:700;'
                f'padding:3px 8px;border-radius:3px;letter-spacing:1px;">● LIVE</span>'
                f'<span style="font-size:1rem;font-weight:600;color:#fff">{m["home_team"]}</span>'
                f'<span class="num" style="font-size:1.3rem;font-weight:700;color:#C9A84C">'
                f'{m["home_score"] or 0} – {m["away_score"] or 0}</span>'
                f'<span style="font-size:1rem;font-weight:600;color:#fff">{m["away_team"]}</span></div>'
                f'<span class="lock-badge">🔒 {m["home_team_code"]} · {m["away_team_code"]} LOCKED</span>'
                f'</div><div style="font-size:0.72rem;color:#3A4060;margin-top:6px">'
                f'{m.get("stage","")} · {m["kickoff_utc"][:16].replace("T"," ")} UTC</div></div>',
                unsafe_allow_html=True
            )

    if upcoming_m:
        st.markdown("## Upcoming Fixtures")
        for m in upcoming_m[:20]:
            ko = m["kickoff_utc"][:16].replace("T"," ")
            st.markdown(
                f'<div class="wc-card">'
                f'<div style="font-size:0.68rem;color:#3A4060;margin-bottom:6px;">'
                f'{m.get("stage","")} · {ko} UTC</div>'
                f'<div style="font-size:0.95rem;font-weight:600;color:#C8D0E0;">'
                f'{m["home_team"]} '
                f'<span style="color:#3A4060">vs</span>'
                f' {m["away_team"]}'
                f'<span style="color:#3A4060;font-size:0.78rem;margin-left:8px">'
                f'{m["home_team_code"]} / {m["away_team_code"]}</span></div></div>',
                unsafe_allow_html=True
            )

    if finished_m:
        st.markdown("## Results — Prices Updated")
        for m in finished_m[:30]:
            proc = m.get("processed",0)
            badge = ('<span style="color:#2ECC71;font-size:0.68rem">✅ Updated</span>'
                     if proc else
                     '<span style="color:#C9A84C;font-size:0.68rem">⏳ Processing</span>')
            ko = m["kickoff_utc"][:16].replace("T"," ")
            st.markdown(
                f'<div class="wc-card" style="opacity:0.8">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div><span style="font-size:0.68rem;color:#3A4060">{m.get("stage","")} · {ko} UTC</span> {badge}<br>'
                f'<span style="font-size:0.95rem;font-weight:600;color:#C8D0E0">'
                f'{m["home_team"]} '
                f'<span class="num" style="color:#C9A84C;font-weight:700">'
                f'{m["home_score"] or "?"} – {m["away_score"] or "?"}</span>'
                f' {m["away_team"]}</span></div></div></div>',
                unsafe_allow_html=True
            )

    if not matches:
        st.markdown(
            '<div class="wc-card" style="text-align:center;padding:40px;">'
            '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.6rem;'
            'letter-spacing:3px;color:#C9A84C;margin-bottom:8px;">TOURNAMENT BEGINS</div>'
            '<div class="num" style="font-size:2.5rem;font-weight:700;color:#fff">11 JUNE 2026</div>'
            '<div style="color:#5A6080;margin-top:8px;font-size:0.85rem">'
            'Mexico vs South Africa · Estadio Azteca · Mexico City</div>'
            '<div style="color:#3A4060;margin-top:16px;font-size:0.78rem">'
            'Add your football-data.org API key to config.py to load the full schedule.</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("## How Pricing Works")
    st.markdown(
        '<div class="wc-card">'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">'
        '<div><div style="font-size:0.68rem;color:#E61D25;text-transform:uppercase;'
        'letter-spacing:0.12em;margin-bottom:6px;">1 · Match Kicks Off</div>'
        '<div style="font-size:0.82rem;color:#8090B0">All players on both teams are immediately locked. '
        'No buying or selling until the final whistle.</div></div>'
        '<div><div style="font-size:0.68rem;color:#C9A84C;text-transform:uppercase;'
        'letter-spacing:0.12em;margin-bottom:6px;">2 · Full Time</div>'
        '<div style="font-size:0.82rem;color:#8090B0">App fetches complete match stats automatically '
        'from football-data.org. Goals, cards, result, clean sheets — all applied at once.</div></div>'
        '<div><div style="font-size:0.68rem;color:#2ECC71;text-transform:uppercase;'
        'letter-spacing:0.12em;margin-bottom:6px;">3 · Prices Update</div>'
        '<div style="font-size:0.82rem;color:#8090B0">Valuation engine applies all rules. '
        'Match rating bonus stacks on top. All changes compound multiplicatively.</div></div>'
        '<div><div style="font-size:0.68rem;color:#2A398D;text-transform:uppercase;'
        'letter-spacing:0.12em;margin-bottom:6px;">4 · Market Reopens</div>'
        '<div style="font-size:0.82rem;color:#8090B0">Trading unlocks. '
        'React to the new prices before the next match.</div></div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    if st.button("🔄 Refresh Schedule"):
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — PORTFOLIO
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💼 My Portfolio":
    if not st.session_state.username:
        st.warning("Enter a username in the sidebar to view your portfolio.")
        st.stop()

    username = st.session_state.username
    user     = db.get_or_create_user(username)
    holdings = db.get_holdings(username)
    locked   = db.get_locked_teams()

    st.title(f"PORTFOLIO")
    st.markdown(f'<div class="page-eyebrow">Manager: {username} · Starting Capital: $700M</div>',
                unsafe_allow_html=True)

    hval   = sum(h["shares"]*h["live_price"] for h in holdings)
    total  = user["cash"] + hval
    roi    = ((total - config.STARTING_CASH) / config.STARTING_CASH) * 100
    unreal = sum(h["shares"]*(h["live_price"]-h["avg_cost"]) for h in holdings)

    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("Total Portfolio", fmil(total))
    m2.metric("Cash Balance",    fmil(user["cash"]))
    m3.metric("Holdings Value",  fmil(hval))
    m4.metric("Unrealised P&L",  fmil(unreal),
              delta=fmil(unreal), delta_color="normal" if unreal>=0 else "inverse")
    m5.metric("ROI",             f"{roi:+.3f}%",
              delta="vs $700M start", delta_color="normal" if roi>=0 else "inverse")

    st.markdown("## Holdings")
    if holdings:
        rows = []
        for h in holdings:
            mv  = h["shares"]*h["live_price"]
            cv  = h["shares"]*h["avg_cost"]
            pl  = mv-cv
            plp = (pl/cv*100) if cv>0 else 0
            rows.append({
                "":        h.get("flag",""),
                "Ticker":  h["player_id"],
                "Player":  h["name"],
                "Pos":     h["pos"],
                "Nation":  h["team"],
                "🔒":      "🔒" if h["team_code"] in locked else "",
                "Shares":  round(h["shares"],2),
                "Avg $":   round(h["avg_cost"],2),
                "Live $":  round(h["live_price"],2),
                "Value $M":round(mv/1e6,3),
                "P&L $":   round(pl,2),
                "P&L %":   round(plp,3),
                "Rating":  round(h["last_rating"],1) if h.get("last_rating") else None,
                "Alloc %": round(mv/total*100,2) if total>0 else 0,
            })
        hdf = pd.DataFrame(rows)
        def _hl_h(row):
            return [f"background-color:{'#051A0C' if row['P&L $']>=0 else '#1A0508'}"]*len(row)
        st.dataframe(
            hdf.style.apply(_hl_h, axis=1)
               .format({"Avg $":"${:.2f}","Live $":"${:.2f}","Value $M":"${:.3f}M",
                        "P&L $":"${:+,.2f}","P&L %":"{:+.3f}%","Alloc %":"{:.2f}%"}, na_rep="—"),
            use_container_width=True, height=380,
        )

        pc1,pc2 = st.columns(2)
        with pc1:
            pie = [{"label":h["player_id"],"value":h["shares"]*h["live_price"]} for h in holdings]
            pie.append({"label":"CASH","value":user["cash"]})
            fig_p = px.pie(pd.DataFrame(pie), values="value", names="label",
                           color_discrete_sequence=["#E61D25","#C9A84C","#2ECC71","#2A398D",
                                                     "#7B68EE","#00BFFF","#FF8C00","#8090B0"])
            fig_p.update_layout(paper_bgcolor="#0B0E1A",font=dict(family="Inter",color="#5A6080"),
                                 margin=dict(l=10,r=10,t=30,b=10),height=300,
                                 legend=dict(bgcolor="#0E122A"),
                                 title=dict(text="Allocation",font=dict(color="#C9A84C",family="Bebas Neue",size=14)))
            st.plotly_chart(fig_p, use_container_width=True)

        with pc2:
            pos_agg = {}
            for h in holdings:
                pos_agg[h["pos"]] = pos_agg.get(h["pos"],0) + h["shares"]*h["live_price"]
            pos_df = pd.DataFrame(list(pos_agg.items()), columns=["Pos","Value"])
            fig_b = px.bar(pos_df,x="Pos",y="Value",color="Pos",
                           color_discrete_map={"ATT":"#E61D25","MID":"#C9A84C","DEF":"#2A398D","GK":"#2ECC71"})
            fig_b.update_layout(paper_bgcolor="#0B0E1A",plot_bgcolor="#0E122A",
                                 font=dict(family="Inter",color="#5A6080"),
                                 yaxis=dict(tickprefix="$",gridcolor="#1C2340"),
                                 xaxis=dict(gridcolor="#1C2340"),
                                 margin=dict(l=10,r=10,t=30,b=10),height=300,showlegend=False,
                                 title=dict(text="By Position",font=dict(color="#C9A84C",family="Bebas Neue",size=14)))
            st.plotly_chart(fig_b, use_container_width=True)
    else:
        st.markdown(
            '<div class="info-box">No holdings yet. Head to the Trade Desk to build your squad!</div>',
            unsafe_allow_html=True
        )

    st.markdown("## Transaction Ledger")
    trades = db.get_trade_history(username, 100)
    if trades:
        tdf = pd.DataFrame([{
            "Time":      t["ts"][:19].replace("T"," "),
            "":          t.get("flag",""),
            "Ticker":    t["player_id"],
            "Player":    t["player_name"],
            "Type":      t["trade_type"],
            "Shares":    round(t["shares"],2),
            "Price $":   round(t["exec_price"],2),
            "Total $":   round(t["total_value"],2),
        } for t in trades])
        def _hl_t(row):
            return [f"background-color:{'#051A0C' if row['Type']=='BUY' else '#1A0508'}"]*len(row)
        st.dataframe(
            tdf.style.apply(_hl_t,axis=1)
               .format({"Price $":"${:.2f}","Total $":"${:,.2f}"}),
            use_container_width=True, height=320,
        )
    else:
        st.markdown('<div class="info-box">No trades yet.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — TRADE DESK
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚡ Trade Desk":
    if not st.session_state.username:
        st.warning("Enter a username in the sidebar to trade.")
        st.stop()

    username = st.session_state.username
    user     = db.get_or_create_user(username)
    players  = db.get_all_players()
    locked   = db.get_locked_teams()

    st.title("TRADE DESK")
    st.markdown(
        f'<div class="page-eyebrow">Account: {username} · Cash: {fmil(user["cash"])} · '
        f'{len(locked)} Teams Locked</div>', unsafe_allow_html=True
    )

    if locked:
        st.markdown(
            f'<div class="lock-box">🔒 Trading suspended for {len(locked)} team(s) currently playing: '
            f'<b>{", ".join(locked)}</b> — Unlocks automatically at full time.</div>',
            unsafe_allow_html=True
        )

    ticker_map = {}
    for p in players:
        lk = " 🔒" if p["team_code"] in locked else ""
        ticker_map[f'{p.get("flag","")} {p["id"]} — {p["name"]} ({p["team"]}) ${p["live_price"]:.2f}{lk}'] = p["id"]

    col_order, col_info = st.columns([1.1, 1])

    with col_order:
        st.markdown("## Order Entry")
        sel_label = st.selectbox("🔍 Select Instrument", list(ticker_map.keys()))
        sel_id    = ticker_map[sel_label]
        player    = db.get_player(sel_id)
        is_locked, lock_reason = db.is_player_locked(sel_id)

        trade_type = st.radio("Order Type", ["BUY","SELL"], horizontal=True)
        shares_qty = st.number_input("Quantity (shares)", min_value=0.01, step=100.0, value=100.0)

        exec_price = player["live_price"]
        total_cost = shares_qty * exec_price
        cash_after = user["cash"] - total_cost if trade_type=="BUY" else user["cash"]+total_cost

        bg = "#120A08" if is_locked else "#0E122A"
        border = "#3A1810" if is_locked else "#1C2340"
        st.markdown(
            f'<div style="background:{bg};border:1px solid {border};border-radius:8px;padding:16px;margin-top:12px;">'
            f'<div style="font-size:0.65rem;color:#3A4060;text-transform:uppercase;'
            f'letter-spacing:0.15em;margin-bottom:12px;">{"🔒 LOCKED — " if is_locked else ""}Order Preview</div>'
            f'<table style="width:100%;font-size:0.84rem;border-spacing:0 6px;">'
            f'<tr><td style="color:#5A6080">Instrument</td>'
            f'<td style="text-align:right;color:#fff;font-weight:600">'
            f'{player.get("flag","")} {player["id"]} — {player["name"]}</td></tr>'
            f'<tr><td style="color:#5A6080">Type</td>'
            f'<td style="text-align:right;color:{"#2ECC71" if trade_type=="BUY" else "#E61D25"};font-weight:700">{trade_type}</td></tr>'
            f'<tr><td style="color:#5A6080">Shares</td>'
            f'<td class="num" style="text-align:right;color:#C8D0E0">{shares_qty:,.2f}</td></tr>'
            f'<tr><td style="color:#5A6080">Exec Price</td>'
            f'<td class="num" style="text-align:right;color:#C9A84C;font-weight:700">${exec_price:.2f}</td></tr>'
            f'<tr><td style="color:#5A6080">Order Value</td>'
            f'<td class="num" style="text-align:right;color:#fff;font-weight:700">{fmil(total_cost)}</td></tr>'
            f'<tr><td style="color:#5A6080">Cash After</td>'
            f'<td class="num" style="text-align:right;color:{"#2ECC71" if cash_after>=0 else "#E61D25"};font-weight:700">'
            f'{fmil(cash_after)}</td></tr>'
            f'</table></div>',
            unsafe_allow_html=True
        )

        st.markdown("")
        if is_locked:
            st.markdown(f'<div class="lock-box">{lock_reason}</div>', unsafe_allow_html=True)
        else:
            btn_label = "🟢 EXECUTE BUY" if trade_type=="BUY" else "🔴 EXECUTE SELL"
            css_class = "btn-green" if trade_type=="BUY" else "btn-sell"
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(btn_label, use_container_width=True):
                ok, msg = db.execute_trade(username, sel_id, trade_type, shares_qty, exec_price)
                if ok:
                    st.markdown(f'<div class="success-box">{msg}</div>', unsafe_allow_html=True)
                    if trade_type == "BUY": st.balloons()
                else:
                    st.markdown(f'<div class="error-box">❌ {msg}</div>', unsafe_allow_html=True)
                time.sleep(0.3)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown("## Instrument Details")
        chg = chg_pct(player)
        ic  = ipo_chg(player)

        st.metric("Live Price", fprice(player["live_price"]))
        st.metric("Session Δ", f"{chg:+.3f}%", delta_color="normal" if chg>=0 else "inverse")
        st.metric("vs IPO",    f"{ic:+.3f}%",  delta_color="normal" if ic>=0 else "inverse")
        st.metric("IPO Price", fprice(player["ipo_price"]))
        st.metric("Volume",    f'{player["volume"]:,} shares')

        if player.get("last_rating"):
            st.markdown(
                f'<div style="margin-top:8px;"><div style="font-size:0.65rem;color:#3A4060;'
                f'text-transform:uppercase;letter-spacing:0.12em;margin-bottom:4px;">Last Match Rating</div>'
                f'{rating_html(player["last_rating"])}</div>',
                unsafe_allow_html=True
            )

        if is_locked:
            st.markdown(f'<div class="lock-box" style="margin-top:10px;">{lock_reason}</div>',
                        unsafe_allow_html=True)

        holdings = db.get_holdings(username)
        my_h = next((h for h in holdings if h["player_id"]==sel_id), None)
        st.markdown("---")
        if my_h:
            mv = my_h["shares"]*player["live_price"]
            pl = my_h["shares"]*(player["live_price"]-my_h["avg_cost"])
            st.markdown(
                f'<div class="wc-card wc-card-gold">'
                f'<div style="font-size:0.65rem;color:#3A4060;text-transform:uppercase;'
                f'letter-spacing:0.12em;margin-bottom:10px;">Your Position</div>'
                f'<table style="width:100%;font-size:0.82rem;">'
                f'<tr><td style="color:#5A6080">Shares</td>'
                f'<td class="num" style="text-align:right;color:#C8D0E0">{my_h["shares"]:,.2f}</td></tr>'
                f'<tr><td style="color:#5A6080">Avg Cost</td>'
                f'<td class="num" style="text-align:right;color:#C8D0E0">${my_h["avg_cost"]:.2f}</td></tr>'
                f'<tr><td style="color:#5A6080">Market Value</td>'
                f'<td class="num" style="text-align:right;color:#C9A84C;font-weight:700">{fmil(mv)}</td></tr>'
                f'<tr><td style="color:#5A6080">P&L</td>'
                f'<td class="num" style="text-align:right;color:{"#2ECC71" if pl>=0 else "#E61D25"};font-weight:700">'
                f'{fmil(pl)}</td></tr></table></div>',
                unsafe_allow_html=True
            )

        hist = db.get_price_history(sel_id, 80)
        if len(hist) > 2:
            hdf_m = pd.DataFrame(hist)
            hdf_m["ts"] = pd.to_datetime(hdf_m["ts"])
            lc_m = "#2ECC71" if hdf_m["price"].iloc[-1]>=hdf_m["price"].iloc[0] else "#E61D25"
            fig_m = go.Figure(go.Scatter(
                x=hdf_m["ts"], y=hdf_m["price"], mode="lines+markers",
                line=dict(color=lc_m,width=1.5), marker=dict(size=4),
                fill="tozeroy",
                fillcolor=f"{'rgba(46,204,113,0.06)' if lc_m=='#2ECC71' else 'rgba(230,29,37,0.06)'}",
            ))
            fig_m.update_layout(
                paper_bgcolor="#0B0E1A",plot_bgcolor="#0E122A",
                margin=dict(l=40,r=10,t=10,b=30),height=170,
                xaxis=dict(gridcolor="#1C2340",showgrid=False),
                yaxis=dict(gridcolor="#1C2340",tickprefix="$"),
                showlegend=False,
            )
            st.plotly_chart(fig_m, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — LEADERBOARD
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🏆 Leaderboard":
    st.title("LEADERBOARD")
    st.markdown('<div class="page-eyebrow">All Managers · Ranked by ROI% · Real-time</div>',
                unsafe_allow_html=True)

    leaders = db.get_leaderboard()
    current = st.session_state.get("username","")

    if not leaders:
        st.markdown('<div class="info-box">No managers yet. Be the first to register!</div>',
                    unsafe_allow_html=True)
    else:
        medals = ["🥇","🥈","🥉"]
        if len(leaders) >= 3:
            p2,p1,p3 = st.columns(3)
            for rank, col in [(1,p2),(0,p1),(2,p3)]:
                if rank < len(leaders):
                    l = leaders[rank]
                    is_me = l["username"]==current
                    border = "border:2px solid #E61D25;" if is_me else "border:1px solid #1C2340;"
                    roi_c  = "#2ECC71" if l["roi_pct"]>=0 else "#E61D25"
                    col.markdown(
                        f'<div class="podium-card" style="{border}">'
                        f'<div class="podium-medal">{medals[rank]}</div>'
                        f'<div class="podium-name">{"▶ " if is_me else ""}{l["username"]}</div>'
                        f'<div class="podium-roi" style="color:{roi_c}">{l["roi_pct"]:+.3f}%</div>'
                        f'<div class="podium-val">{fmil(l["total_value"])}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        st.markdown("## Full Rankings")
        lb_rows = []
        for i,l in enumerate(leaders):
            is_me = l["username"]==current
            lb_rows.append({
                "Rank":         i+1,
                "Manager":      ("▶ " if is_me else "")+l["username"],
                "Total ($M)":   round(l["total_value"]/1e6,3),
                "Holdings ($M)":round(l["holdings_value"]/1e6,3),
                "Cash ($M)":    round(l["cash"]/1e6,3),
                "ROI %":        round(l["roi_pct"],4),
            })
        lb_df = pd.DataFrame(lb_rows)
        def _hl_lb(row):
            if current and current in row["Manager"]: return ["background-color:#0D1830"]*len(row)
            return [f"background-color:{'#051A0C' if row['ROI %']>0 else '#1A0508' if row['ROI %']<0 else ''}"]*len(row)
        st.dataframe(
            lb_df.style.apply(_hl_lb,axis=1)
                 .format({"Total ($M)":"${:.3f}M","Holdings ($M)":"${:.3f}M",
                          "Cash ($M)":"${:.3f}M","ROI %":"{:+.4f}%"}),
            use_container_width=True, height=400,
        )

        if len(leaders)>1:
            fig_lb = px.bar(
                pd.DataFrame(leaders), x="username", y="roi_pct",
                color="roi_pct",
                color_continuous_scale=["#E61D25","#1C2340","#2ECC71"],
                color_continuous_midpoint=0,
                labels={"roi_pct":"ROI %","username":"Manager"},
            )
            fig_lb.update_layout(
                paper_bgcolor="#0B0E1A",plot_bgcolor="#0E122A",
                font=dict(family="Inter",color="#5A6080",size=11),
                yaxis=dict(gridcolor="#1C2340",ticksuffix="%"),
                xaxis=dict(gridcolor="#1C2340"),
                margin=dict(l=40,r=20,t=30,b=40),height=260,
                coloraxis_showscale=False,
                title=dict(text="ROI Comparison",font=dict(color="#C9A84C",size=14,family="Bebas Neue")),
            )
            st.plotly_chart(fig_lb, use_container_width=True)

    if st.button("🔄 Refresh Leaderboard"):
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — ADMIN PANEL
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔧 Admin Panel":
    st.title("ADMIN PANEL")
    st.markdown('<div class="page-eyebrow">System Control · API · Manual Match Entry</div>',
                unsafe_allow_html=True)

    # ── Password protection ───────────────────────────────────────────────────
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "wc26admin")

    if "admin_unlocked" not in st.session_state:
        st.session_state.admin_unlocked = False

    if not st.session_state.admin_unlocked:
        st.markdown(
            '<div class="wc-card" style="max-width:400px;margin:60px auto;text-align:center;">'
            '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.4rem;'
            'letter-spacing:3px;color:#C9A84C;margin-bottom:16px;">🔒 ADMIN ACCESS</div>'
            '<div style="font-size:0.82rem;color:#5A6080;margin-bottom:16px;">'
            'This panel is restricted to the tournament administrator only.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        pwd = st.text_input("Enter admin password", type="password", key="admin_pwd")
        if st.button("Unlock Admin Panel"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_unlocked = True
                st.rerun()
            else:
                st.markdown(
                    '<div class="error-box">❌ Incorrect password.</div>',
                    unsafe_allow_html=True
                )
        st.stop()

    st.markdown("## API Configuration")
    bbs_ready = config.BBS_API_KEY and config.BBS_API_KEY != "YOUR_BBS_KEY_HERE"
    if bbs_ready:
        st.markdown(
            '<div class="success-box">✅ Big Balls Data API key configured — '
            'live WC2026 data active from 11 June 2026</div>',
            unsafe_allow_html=True
        )
        ac1, ac2 = st.columns(2)
        with ac1:
            if st.button("📥 Fetch Full WC2026 Schedule"):
                with st.spinner("Fetching all 104 fixtures…"):
                    count = api.fetch_schedule()
                st.success(f"Loaded {count} fixtures")
                st.rerun()
        with ac2:
            if st.button("🔄 Check & Process Matches Now"):
                with st.spinner("Checking live + finished matches…"):
                    api.update_match_statuses()
                    results = api.process_finished_matches()
                st.success(f"Processed {len(results)} player price updates")
                st.rerun()
    else:
        st.markdown(
            '<div class="lock-box">⚪ Big Balls Data API key not set.<br>'
            '<b>Step 1:</b> Sign up free at <b>bigballsdata.com/signup</b> (no card needed)<br>'
            '<b>Step 2:</b> Open config.py, find BBS_API_KEY and paste your key<br>'
            '<b>Step 3:</b> Restart the app — everything activates automatically</div>',
            unsafe_allow_html=True
        )

    st.markdown("## Enter Real Match Result Manually")
    st.markdown(
        '<div class="info-box">Use when the API misses a result or you want to enter '
        'data yourself. You can also add individual events like goals and cards below.</div>',
        unsafe_allow_html=True
    )

    players = db.get_all_players()
    teams   = sorted(set(p["team"] for p in players))
    tc_map  = {p["team"]: p["team_code"] for p in players}

    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        home_team  = st.selectbox("Home Team", teams, key="ht")
        home_goals = st.number_input("Home Goals", min_value=0, max_value=15, value=1, key="hg")
    with mc2:
        away_team  = st.selectbox("Away Team", [t for t in teams if t != home_team], key="at")
        away_goals = st.number_input("Away Goals", min_value=0, max_value=15, value=0, key="ag")
    with mc3:
        stage_sel = st.selectbox("Stage", ["GROUP_STAGE","ROUND_OF_16","QUARTER_FINALS",
                                            "SEMI_FINALS","FINAL"])
        is_ko = stage_sel != "GROUP_STAGE"

    if st.button("📊 Process This Result", use_container_width=False):
        hc  = tc_map.get(home_team, home_team[:3].upper())
        ac  = tc_map.get(away_team, away_team[:3].upper())
        now = datetime.now(timezone.utc).isoformat()
        conn = db.get_conn()
        conn.execute("""INSERT INTO matches
            (home_team,home_team_code,away_team,away_team_code,
             kickoff_utc,stage,status,home_score,away_score,processed)
            VALUES (?,?,?,?,?,?,'FINISHED',?,?,0)""",
            (home_team,hc,away_team,ac,now,stage_sel,home_goals,away_goals))
        conn.commit()
        mid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        with st.spinner("Processing all player prices…"):
            results = api.process_manual_match(mid, hc, ac, home_goals, away_goals, is_ko)
        st.success(f"✅ {len(results)} player prices updated")
        st.rerun()

    st.markdown("---")

    # ── Single event injection ────────────────────────────────────────────────
    st.markdown("## ⚡ Inject a Single Event")
    st.markdown(
        '<div class="info-box">Use this to correct a specific player price. '
        'For example: API missed a goal, a player got injured, or any unusual situation. '
        'You can use standard events OR set a custom % change directly.</div>',
        unsafe_allow_html=True
    )

    ticker_map_admin = {
        f'{p.get("flag","")} {p["id"]} — {p["name"]} ({p["team"]})': p["id"]
        for p in players
    }

    ev1, ev2, ev3 = st.columns(3)
    with ev1:
        ev_player_label = st.selectbox("Player", list(ticker_map_admin.keys()), key="ev_player")
        ev_player_id    = ticker_map_admin[ev_player_label]
        ev_player       = db.get_player(ev_player_id)

    with ev2:
        event_options = [
            "GOAL", "ASSIST", "YELLOW_CARD", "RED_CARD", "OWN_GOAL",
            "PENALTY_MISS", "CLEAN_SHEET", "SAVE", "TACKLE",
            "GOAL_CONCEDED", "ERROR_TO_GOAL", "BIG_CHANCE_MISSED",
            "TEAM_WIN", "TEAM_ADVANCE", "TEAM_ELIMINATED",
            "PASS_ACC_90", "CUSTOM_%",
        ]
        ev_type = st.selectbox("Event Type", event_options, key="ev_type")

    with ev3:
        ev_desc = st.text_input("Description", placeholder="e.g. 78' header vs France", key="ev_desc")
        if ev_type == "CUSTOM_%":
            custom_pct = st.number_input("Custom % change", min_value=-50.0,
                                          max_value=50.0, value=0.0, step=0.5, key="ev_pct")
        else:
            custom_pct = None

    # Show what the standard % would be for info
    standard_pcts = {
        "GOAL":"+5%","ASSIST":"+3%","YELLOW_CARD":"-1%","RED_CARD":"-5%",
        "OWN_GOAL":"-6%","PENALTY_MISS":"-4%","CLEAN_SHEET":"+5%","SAVE":"+1.5%",
        "TACKLE":"+1%","GOAL_CONCEDED":"-2%","ERROR_TO_GOAL":"-5%",
        "BIG_CHANCE_MISSED":"-2%","TEAM_WIN":"+1%","TEAM_ADVANCE":"+3%",
        "TEAM_ELIMINATED":"-4%","PASS_ACC_90":"+3%",
    }
    if ev_type != "CUSTOM_%" and ev_player:
        std = standard_pcts.get(ev_type, "varies")
        cur = ev_player["live_price"]
        st.markdown(
            f'<div style="font-size:0.78rem;color:#5A6080;margin-top:4px;">'
            f'Standard impact: <span style="color:#C9A84C">{std}</span> · '
            f'Current price: <span style="color:#C9A84C">${cur:.2f}</span></div>',
            unsafe_allow_html=True
        )

    if st.button("🔥 Apply Event Now", use_container_width=False):
        result = api.apply_single_manual_event(
            ev_player_id, ev_type,
            custom_pct=custom_pct if ev_type == "CUSTOM_%" else None,
            description=ev_desc
        )
        if result:
            direction = "▲" if result.total_delta_pct > 0 else "▼"
            st.markdown(
                f'<div class="success-box">'
                f'{direction} <b>{result.player_name}</b> [{ev_type}]<br>'
                f'${result.old_price:.2f} → ${result.new_price:.2f} '
                f'({result.total_delta_pct:+.2f}%)<br>'
                f'{ev_desc}</div>',
                unsafe_allow_html=True
            )
            st.rerun()
        else:
            st.markdown(
                '<div class="error-box">❌ Could not apply event — '
                'check player position matches event type.</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ── Direct price edit ─────────────────────────────────────────────────────
    st.markdown("## ✏️ Edit Player Price Directly")
    st.markdown(
        '<div class="info-box">Override a player\'s price to an exact value. '
        'Use only if something has gone badly wrong and needs an immediate fix.</div>',
        unsafe_allow_html=True
    )

    pe1, pe2, pe3 = st.columns(3)
    with pe1:
        edit_label  = st.selectbox("Player", list(ticker_map_admin.keys()), key="edit_player")
        edit_id     = ticker_map_admin[edit_label]
        edit_player = db.get_player(edit_id)
    with pe2:
        new_price_val = st.number_input(
            "New Price ($)",
            min_value=0.50, max_value=500.0,
            value=float(edit_player["live_price"]) if edit_player else 50.0,
            step=0.50, key="edit_price"
        )
    with pe3:
        edit_reason = st.text_input("Reason", placeholder="e.g. Manual correction", key="edit_reason")

    if st.button("💾 Set Price", use_container_width=False):
        if edit_player:
            db.update_player_price(edit_id, new_price_val,
                                   reason=f"MANUAL_EDIT: {edit_reason}")
            st.success(f"✅ {edit_player['name']} price set to ${new_price_val:.2f}")
            st.rerun()

    st.markdown("## Lock / Unlock Teams")
    lc1,lc2 = st.columns(2)
    locked = db.get_locked_teams()
    with lc1:
        all_codes = sorted(set(p["team_code"] for p in players))
        lock_t = st.selectbox("Lock team", all_codes)
        if st.button(f"🔒 Lock {lock_t}"):
            conn = db.get_conn()
            conn.execute("INSERT OR REPLACE INTO trading_locks (team_code,match_id,locked_at) VALUES (?,0,?)",
                         (lock_t, datetime.now(timezone.utc).isoformat()))
            conn.commit(); conn.close()
            st.rerun()
    with lc2:
        if locked:
            unlock_t = st.selectbox("Unlock team", sorted(locked))
            if st.button(f"🔓 Unlock {unlock_t}"):
                conn = db.get_conn()
                conn.execute("DELETE FROM trading_locks WHERE team_code=?", (unlock_t,))
                conn.commit(); conn.close()
                st.rerun()
        else:
            st.info("No teams currently locked.")

    st.markdown("## Recent Price Events")
    events = db.get_recent_events(60)
    if events:
        edf = pd.DataFrame([{
            "Time":   e["ts"][:19].replace("T"," "),
            "":       e.get("flag",""),
            "Player": e["player_name"],
            "Pos":    e["pos"],
            "Event":  e["event_type"],
            "Δ%":     round(e["delta_pct"],2),
            "Note":   e.get("description",""),
        } for e in events])
        def _hl_ev(row):
            return [f"background-color:{'#051A0C' if row['Δ%']>0 else '#1A0508'}"]*len(row)
        st.dataframe(
            edf.style.apply(_hl_ev,axis=1).format({"Δ%":"{:+.2f}%"}),
            use_container_width=True, height=360,
        )

    st.markdown("## Reset Market")
    with st.expander("⚠️ Danger Zone"):
        confirm = st.text_input("Type RESET to confirm")
        if st.button("Reset All Prices to IPO") and confirm=="RESET":
            conn = db.get_conn()
            conn.execute("UPDATE players SET live_price=ipo_price,prev_price=ipo_price,volume=0,last_rating=NULL")
            conn.execute("DELETE FROM price_history")
            conn.execute("DELETE FROM match_events")
            conn.execute("DELETE FROM trading_locks")
            conn.execute("DELETE FROM matches")
            from datetime import datetime as dt
            now = datetime.now(timezone.utc).isoformat()
            for p in conn.execute("SELECT id,ipo_price FROM players").fetchall():
                conn.execute("INSERT INTO price_history (player_id,price,reason,ts) VALUES (?,?,'IPO',?)",
                             (p["id"],p["ipo_price"],now))
            conn.commit(); conn.close()
            st.success("✅ Market reset to IPO prices")
            st.rerun()
