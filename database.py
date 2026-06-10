"""
database.py — SQLite persistence layer for WC26 Equity Terminal
"""

import sqlite3, os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "terminal.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    from data.players_seed import PLAYERS_SEED
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS players (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, pos TEXT NOT NULL,
        team TEXT NOT NULL, team_code TEXT NOT NULL, flag TEXT NOT NULL,
        ipo_price REAL NOT NULL, live_price REAL NOT NULL, prev_price REAL NOT NULL,
        volume INTEGER DEFAULT 0, last_rating REAL, last_update TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT NOT NULL,
        price REAL NOT NULL, reason TEXT, ts TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, cash REAL NOT NULL DEFAULT 700000000.0,
        created_at TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS portfolios (
        username TEXT NOT NULL, player_id TEXT NOT NULL,
        shares REAL NOT NULL DEFAULT 0, avg_cost REAL NOT NULL DEFAULT 0,
        PRIMARY KEY (username, player_id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL,
        player_id TEXT NOT NULL, trade_type TEXT NOT NULL, shares REAL NOT NULL,
        exec_price REAL NOT NULL, total_value REAL NOT NULL, ts TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT, api_fixture_id INTEGER UNIQUE,
        home_team TEXT NOT NULL, home_team_code TEXT NOT NULL,
        away_team TEXT NOT NULL, away_team_code TEXT NOT NULL,
        kickoff_utc TEXT NOT NULL, stage TEXT, status TEXT DEFAULT 'SCHEDULED',
        home_score INTEGER, away_score INTEGER, processed INTEGER DEFAULT 0,
        last_checked TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS match_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT, match_id INTEGER, player_id TEXT NOT NULL,
        event_type TEXT NOT NULL, delta_pct REAL NOT NULL, description TEXT, ts TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS trading_locks (
        team_code TEXT PRIMARY KEY, match_id INTEGER NOT NULL, locked_at TEXT NOT NULL
    )""")

    conn.commit()

    if c.execute("SELECT COUNT(*) FROM players").fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        for p in PLAYERS_SEED:
            c.execute("""INSERT OR IGNORE INTO players
                (id,name,pos,team,team_code,flag,ipo_price,live_price,prev_price,volume,last_update)
                VALUES (?,?,?,?,?,?,?,?,?,0,?)""",
                (p["id"],p["name"],p["pos"],p["team"],p["team_code"],p.get("flag",""),
                 p["ipo"],p["ipo"],p["ipo"],now))
            c.execute("INSERT INTO price_history (player_id,price,reason,ts) VALUES (?,?,'IPO',?)",
                      (p["id"],p["ipo"],now))
        conn.commit()
    conn.close()


# ── Lock helpers ──────────────────────────────────────────────────────────────
def lock_teams(match_id, home_code, away_code):
    conn = get_conn()
    now = datetime.now(timezone.utc).isoformat()
    for code in [home_code, away_code]:
        conn.execute("INSERT OR REPLACE INTO trading_locks (team_code,match_id,locked_at) VALUES (?,?,?)",
                     (code, match_id, now))
    conn.commit(); conn.close()

def unlock_teams(home_code, away_code):
    conn = get_conn()
    conn.execute("DELETE FROM trading_locks WHERE team_code IN (?,?)", (home_code, away_code))
    conn.commit(); conn.close()

def get_locked_teams():
    conn = get_conn()
    rows = conn.execute("SELECT team_code FROM trading_locks").fetchall()
    conn.close()
    return {r["team_code"] for r in rows}

def is_player_locked(player_id):
    p = get_player(player_id)
    if not p: return False, ""
    locked = get_locked_teams()
    if p["team_code"] in locked:
        return True, f"{p['team']} are currently playing — trading locked until full time."
    return False, ""


# ── Match helpers ─────────────────────────────────────────────────────────────
def upsert_match(api_fixture_id, home_team, home_code, away_team, away_code,
                 kickoff_utc, stage, status, home_score=None, away_score=None):
    conn = get_conn()
    conn.execute("""INSERT INTO matches
        (api_fixture_id,home_team,home_team_code,away_team,away_team_code,
         kickoff_utc,stage,status,home_score,away_score,last_checked)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(api_fixture_id) DO UPDATE SET
        status=excluded.status, home_score=excluded.home_score,
        away_score=excluded.away_score, last_checked=excluded.last_checked""",
        (api_fixture_id,home_team,home_code,away_team,away_code,
         kickoff_utc,stage,status,home_score,away_score,datetime.now(timezone.utc).isoformat()
    conn.commit(); conn.close()

def get_all_matches(limit=104):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM matches ORDER BY kickoff_utc ASC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_live_matches():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM matches WHERE status IN ('IN_PLAY','PAUSED') ORDER BY kickoff_utc").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_upcoming_matches(limit=10):
    conn = get_conn()
    rows = conn.execute("""SELECT * FROM matches WHERE status IN ('SCHEDULED','TIMED')
        ORDER BY kickoff_utc ASC LIMIT ?""", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_finished_unprocessed():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM matches WHERE status IN ('FINISHED','AWARDED') AND processed=0").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_match_processed(match_id):
    conn = get_conn()
    conn.execute("UPDATE matches SET processed=1 WHERE id=?", (match_id,))
    conn.commit(); conn.close()


# ── Player helpers ────────────────────────────────────────────────────────────
def get_all_players():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM players ORDER BY live_price DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_player(player_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM players WHERE id=?", (player_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_players_by_team(team_code):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM players WHERE team_code=?", (team_code,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_player_price(player_id, new_price, reason="", rating=None):
    conn = get_conn()
    now = datetime.now(timezone.utc).isoformat()
    if rating is not None:
        conn.execute("""UPDATE players SET prev_price=live_price, live_price=?,
            last_rating=?, last_update=? WHERE id=?""",
            (round(new_price,4), rating, now, player_id))
    else:
        conn.execute("UPDATE players SET prev_price=live_price, live_price=?, last_update=? WHERE id=?",
            (round(new_price,4), now, player_id))
    conn.execute("INSERT INTO price_history (player_id,price,reason,ts) VALUES (?,?,?,?)",
        (player_id, round(new_price,4), reason, now))
    conn.commit(); conn.close()

def log_match_event(match_id, player_id, event_type, delta_pct, description=""):
    conn = get_conn()
    conn.execute("""INSERT INTO match_events (match_id,player_id,event_type,delta_pct,description,ts)
        VALUES (?,?,?,?,?,?)""",
        (match_id, player_id, event_type, delta_pct, description, datetime.now(timezone.utc).isoformat()
    conn.commit(); conn.close()

def get_price_history(player_id, limit=300):
    conn = get_conn()
    rows = conn.execute("""SELECT price,reason,ts FROM price_history
        WHERE player_id=? ORDER BY id DESC LIMIT ?""", (player_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]

def get_recent_events(limit=60):
    conn = get_conn()
    rows = conn.execute("""SELECT me.*, p.name as player_name, p.pos, p.team, p.flag
        FROM match_events me JOIN players p ON me.player_id=p.id
        ORDER BY me.id DESC LIMIT ?""", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── User helpers ──────────────────────────────────────────────────────────────
def get_or_create_user(username):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    if not row:
        now = datetime.now(timezone.utc).isoformat()
        conn.execute("INSERT INTO users (username,cash,created_at) VALUES (?,?,?)",
                     (username, 700_000_000.0, now))
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row)

def get_all_users():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users ORDER BY username").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Portfolio helpers ─────────────────────────────────────────────────────────
def get_holdings(username):
    conn = get_conn()
    rows = conn.execute("""SELECT po.*, pl.name, pl.pos, pl.team, pl.team_code,
        pl.flag, pl.live_price, pl.ipo_price, pl.last_rating
        FROM portfolios po JOIN players pl ON po.player_id=pl.id
        WHERE po.username=? AND po.shares>0
        ORDER BY (po.shares*pl.live_price) DESC""", (username,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def execute_trade(username, player_id, trade_type, shares, exec_price):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    total_value = shares * exec_price
    try:
        locked, lock_reason = is_player_locked(player_id)
        if locked:
            return False, f"🔒 {lock_reason}"
        user = c.execute("SELECT cash FROM users WHERE username=?", (username,)).fetchone()
        if not user: return False, "User not found."
        cash = user["cash"]

        if trade_type == "BUY":
            if total_value > cash:
                return False, f"Insufficient funds. Need ${total_value:,.2f}, have ${cash:,.2f}."
            c.execute("UPDATE users SET cash=? WHERE username=?", (cash - total_value, username))
            existing = c.execute("SELECT shares,avg_cost FROM portfolios WHERE username=? AND player_id=?",
                                 (username, player_id)).fetchone()
            if existing:
                ns = existing["shares"] + shares
                na = ((existing["shares"] * existing["avg_cost"]) + total_value) / ns
                c.execute("UPDATE portfolios SET shares=?,avg_cost=? WHERE username=? AND player_id=?",
                          (ns, na, username, player_id))
            else:
                c.execute("INSERT INTO portfolios (username,player_id,shares,avg_cost) VALUES (?,?,?,?)",
                          (username, player_id, shares, exec_price))

        elif trade_type == "SELL":
            existing = c.execute("SELECT shares FROM portfolios WHERE username=? AND player_id=?",
                                 (username, player_id)).fetchone()
            if not existing or existing["shares"] < shares:
                held = existing["shares"] if existing else 0
                return False, f"Not enough shares. You hold {held:.2f}, trying to sell {shares:.2f}."
            c.execute("UPDATE portfolios SET shares=? WHERE username=? AND player_id=?",
                      (existing["shares"] - shares, username, player_id))
            c.execute("UPDATE users SET cash=? WHERE username=?", (cash + total_value, username))
        else:
            return False, "Invalid trade type."

        c.execute("""INSERT INTO trades (username,player_id,trade_type,shares,exec_price,total_value,ts)
            VALUES (?,?,?,?,?,?,?)""", (username,player_id,trade_type,shares,exec_price,total_value,now))
        c.execute("UPDATE players SET volume=volume+? WHERE id=?", (int(shares), player_id))
        conn.commit()
        return True, f"✅ {trade_type} {shares:,.2f} shares @ ${exec_price:.2f} = ${total_value:,.2f}"
    except Exception as e:
        conn.rollback()
        return False, f"Trade error: {str(e)}"
    finally:
        conn.close()

def get_trade_history(username, limit=100):
    conn = get_conn()
    rows = conn.execute("""SELECT t.*, p.name as player_name, p.pos, p.team, p.flag
        FROM trades t JOIN players p ON t.player_id=p.id
        WHERE t.username=? ORDER BY t.id DESC LIMIT ?""", (username, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Leaderboard ───────────────────────────────────────────────────────────────
def get_leaderboard():
    conn = get_conn()
    users = conn.execute("SELECT username,cash FROM users").fetchall()
    result = []
    for u in users:
        hval = conn.execute("""SELECT COALESCE(SUM(po.shares*pl.live_price),0) as hval
            FROM portfolios po JOIN players pl ON po.player_id=pl.id
            WHERE po.username=?""", (u["username"],)).fetchone()["hval"]
        total = u["cash"] + hval
        roi = ((total - 700_000_000) / 700_000_000) * 100
        result.append({"username":u["username"],"cash":u["cash"],
                        "holdings_value":hval,"total_value":total,"roi_pct":roi})
    conn.close()
    return sorted(result, key=lambda x: x["roi_pct"], reverse=True)
