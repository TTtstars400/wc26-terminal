"""
database.py — Supabase PostgreSQL persistence layer
Replaces SQLite entirely. Works on Streamlit Cloud permanently.
All data persists across restarts and redeployments.
"""

import os
from datetime import datetime, timezone
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://auxwwwukaqqmoubeisoo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEY", "sb_secret_qifI9kvgaE-q1UNvlFi_4g_FfCSs0Dp")

_client: Client | None = None

def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def init_db():
    from data.players_seed import PLAYERS_SEED
    sb = get_client()
    try:
        existing = sb.table("players").select("id").limit(1).execute()
        if not existing.data:
            now = now_iso()
            for p in PLAYERS_SEED:
                try:
                    sb.table("players").upsert({
                        "id": p["id"], "name": p["name"], "pos": p["pos"],
                        "team": p["team"], "team_code": p["team_code"],
                        "flag": p.get("flag", ""),
                        "ipo_price": p["ipo"], "live_price": p["ipo"],
                        "prev_price": p["ipo"], "volume": 0,
                        "last_update": now
                    }).execute()
                    sb.table("price_history").insert({
                        "player_id": p["id"], "price": p["ipo"],
                        "reason": "IPO", "ts": now
                    }).execute()
                except Exception as e:
                    print(f"[DB] Seed error {p['id']}: {e}")
    except Exception as e:
        print(f"[DB] Init error: {e}")

def lock_teams(match_id, home_code, away_code):
    sb = get_client()
    now = now_iso()
    for code in [home_code, away_code]:
        try:
            sb.table("trading_locks").upsert({"team_code": code, "match_id": match_id, "locked_at": now}).execute()
        except Exception as e:
            print(f"[DB] Lock error: {e}")

def unlock_teams(home_code, away_code):
    sb = get_client()
    for code in [home_code, away_code]:
        try:
            sb.table("trading_locks").delete().eq("team_code", code).execute()
        except Exception as e:
            print(f"[DB] Unlock error: {e}")

def get_locked_teams() -> set:
    sb = get_client()
    try:
        rows = sb.table("trading_locks").select("team_code").execute()
        return {r["team_code"] for r in rows.data}
    except:
        return set()

def is_player_locked(player_id) -> tuple:
    p = get_player(player_id)
    if not p: return False, ""
    locked = get_locked_teams()
    if p["team_code"] in locked:
        return True, f"{p['team']} are currently playing — trading locked until full time."
    return False, ""

def upsert_match(api_fixture_id, home_team, home_code, away_team, away_code,
                 kickoff_utc, stage, status, home_score=None, away_score=None):
    sb = get_client()
    try:
        sb.table("matches").upsert({
            "api_fixture_id": api_fixture_id,
            "home_team": home_team, "home_team_code": home_code,
            "away_team": away_team, "away_team_code": away_code,
            "kickoff_utc": kickoff_utc, "stage": stage, "status": status,
            "home_score": home_score, "away_score": away_score,
            "last_checked": now_iso()
        }, on_conflict="api_fixture_id").execute()
    except Exception as e:
        print(f"[DB] Upsert match error: {e}")

def get_all_matches(limit=104) -> list:
    sb = get_client()
    try:
        rows = sb.table("matches").select("*").order("kickoff_utc").limit(limit).execute()
        return rows.data or []
    except:
        return []

def get_live_matches() -> list:
    sb = get_client()
    try:
        rows = sb.table("matches").select("*").in_("status", ["IN_PLAY","PAUSED"]).execute()
        return rows.data or []
    except:
        return []

def get_upcoming_matches(limit=10) -> list:
    sb = get_client()
    try:
        rows = sb.table("matches").select("*").in_("status", ["SCHEDULED","TIMED"]).order("kickoff_utc").limit(limit).execute()
        return rows.data or []
    except:
        return []

def get_finished_unprocessed() -> list:
    sb = get_client()
    try:
        rows = sb.table("matches").select("*").in_("status", ["FINISHED","AWARDED"]).eq("processed", 0).execute()
        return rows.data or []
    except:
        return []

def mark_match_processed(match_id):
    sb = get_client()
    try:
        sb.table("matches").update({"processed": 1}).eq("id", match_id).execute()
    except Exception as e:
        print(f"[DB] Mark processed error: {e}")

def get_all_players() -> list:
    sb = get_client()
    try:
        rows = sb.table("players").select("*").order("live_price", desc=True).execute()
        return rows.data or []
    except:
        return []

def get_player(player_id) -> dict | None:
    sb = get_client()
    try:
        rows = sb.table("players").select("*").eq("id", player_id).execute()
        return rows.data[0] if rows.data else None
    except:
        return None

def get_players_by_team(team_code) -> list:
    sb = get_client()
    try:
        rows = sb.table("players").select("*").eq("team_code", team_code).execute()
        return rows.data or []
    except:
        return []

def update_player_price(player_id, new_price, reason="", rating=None):
    sb = get_client()
    now = now_iso()
    try:
        player = get_player(player_id)
        if not player: return
        update_data = {
            "prev_price": player["live_price"],
            "live_price": round(new_price, 4),
            "last_update": now
        }
        if rating is not None:
            update_data["last_rating"] = rating
        sb.table("players").update(update_data).eq("id", player_id).execute()
        sb.table("price_history").insert({
            "player_id": player_id, "price": round(new_price, 4),
            "reason": reason, "ts": now
        }).execute()
    except Exception as e:
        print(f"[DB] Update price error: {e}")

def log_match_event(match_id, player_id, event_type, delta_pct, description=""):
    sb = get_client()
    try:
        sb.table("match_events").insert({
            "match_id": match_id, "player_id": player_id,
            "event_type": event_type, "delta_pct": delta_pct,
            "description": description, "ts": now_iso()
        }).execute()
    except Exception as e:
        print(f"[DB] Log event error: {e}")

def get_price_history(player_id, limit=300) -> list:
    sb = get_client()
    try:
        rows = sb.table("price_history").select("price,reason,ts").eq("player_id", player_id).order("id", desc=True).limit(limit).execute()
        return list(reversed(rows.data or []))
    except:
        return []

def get_recent_events(limit=60) -> list:
    sb = get_client()
    try:
        rows = sb.table("match_events").select("*").order("id", desc=True).limit(limit).execute()
        events = rows.data or []
        for ev in events:
            p = get_player(ev["player_id"])
            if p:
                ev["player_name"] = p["name"]
                ev["pos"]         = p["pos"]
                ev["team"]        = p["team"]
                ev["flag"]        = p.get("flag", "")
        return events
    except:
        return []

def get_or_create_user(username: str, password: str = "") -> dict:
    sb = get_client()
    try:
        rows = sb.table("users").select("*").eq("username", username).execute()
        if rows.data:
            return rows.data[0]
        new_user = {
            "username": username, "cash": 700_000_000.0,
            "password": password, "created_at": now_iso()
        }
        sb.table("users").insert(new_user).execute()
        return new_user
    except Exception as e:
        print(f"[DB] User error: {e}")
        return {"username": username, "cash": 700_000_000.0, "password": password}

def verify_user_password(username: str, password: str) -> tuple:
    sb = get_client()
    try:
        rows = sb.table("users").select("*").eq("username", username).execute()
        if not rows.data:
            sb.table("users").insert({
                "username": username, "cash": 700_000_000.0,
                "password": password, "created_at": now_iso()
            }).execute()
            return True, "new_user"
        user = rows.data[0]
        stored_pwd = user.get("password", "")
        if not stored_pwd:
            sb.table("users").update({"password": password}).eq("username", username).execute()
            return True, "password_set"
        if stored_pwd == password:
            return True, "ok"
        return False, "wrong_password"
    except Exception as e:
        return False, str(e)

def get_holdings(username: str) -> list:
    sb = get_client()
    try:
        rows = sb.table("portfolios").select("*").eq("username", username).gt("shares", 0).execute()
        holdings = rows.data or []
        for h in holdings:
            p = get_player(h["player_id"])
            if p:
                h["name"]        = p["name"]
                h["pos"]         = p["pos"]
                h["team"]        = p["team"]
                h["team_code"]   = p["team_code"]
                h["flag"]        = p.get("flag", "")
                h["live_price"]  = p["live_price"]
                h["ipo_price"]   = p["ipo_price"]
                h["last_rating"] = p.get("last_rating")
        holdings.sort(key=lambda x: x.get("shares", 0) * x.get("live_price", 0), reverse=True)
        return holdings
    except Exception as e:
        print(f"[DB] Holdings error: {e}")
        return []

def execute_trade(username: str, player_id: str, trade_type: str,
                  shares: float, exec_price: float) -> tuple:
    sb = get_client()
    total_value = shares * exec_price
    try:
        locked, lock_reason = is_player_locked(player_id)
        if locked:
            return False, f"🔒 {lock_reason}"
        user_rows = sb.table("users").select("cash").eq("username", username).execute()
        if not user_rows.data:
            return False, "User not found."
        cash = user_rows.data[0]["cash"]
        if trade_type == "BUY":
            if total_value > cash:
                return False, f"Insufficient funds. Need ${total_value:,.2f}, have ${cash:,.2f}."
            sb.table("users").update({"cash": cash - total_value}).eq("username", username).execute()
            existing = sb.table("portfolios").select("shares,avg_cost").eq("username", username).eq("player_id", player_id).execute()
            if existing.data:
                old_s = existing.data[0]["shares"]
                old_c = existing.data[0]["avg_cost"]
                new_s = old_s + shares
                new_a = ((old_s * old_c) + total_value) / new_s
                sb.table("portfolios").update({"shares": new_s, "avg_cost": new_a}).eq("username", username).eq("player_id", player_id).execute()
            else:
                sb.table("portfolios").insert({
                    "username": username, "player_id": player_id,
                    "shares": shares, "avg_cost": exec_price
                }).execute()
        elif trade_type == "SELL":
            existing = sb.table("portfolios").select("shares").eq("username", username).eq("player_id", player_id).execute()
            if not existing.data or existing.data[0]["shares"] < shares:
                held = existing.data[0]["shares"] if existing.data else 0
                return False, f"Not enough shares. You hold {held:.2f}, trying to sell {shares:.2f}."
            sb.table("portfolios").update({"shares": existing.data[0]["shares"] - shares}).eq("username", username).eq("player_id", player_id).execute()
            sb.table("users").update({"cash": cash + total_value}).eq("username", username).execute()
        else:
            return False, "Invalid trade type."
        sb.table("trades").insert({
            "username": username, "player_id": player_id,
            "trade_type": trade_type, "shares": shares,
            "exec_price": exec_price, "total_value": total_value,
            "ts": now_iso()
        }).execute()
        player = get_player(player_id)
        if player:
            sb.table("players").update({"volume": player.get("volume", 0) + int(shares)}).eq("id", player_id).execute()
        return True, f"✅ {trade_type} {shares:,.2f} shares @ ${exec_price:.2f} = ${total_value:,.2f}"
    except Exception as e:
        return False, f"Trade error: {str(e)}"

def get_trade_history(username: str, limit: int = 100) -> list:
    sb = get_client()
    try:
        rows = sb.table("trades").select("*").eq("username", username).order("id", desc=True).limit(limit).execute()
        trades = rows.data or []
        for t in trades:
            p = get_player(t["player_id"])
            if p:
                t["player_name"] = p["name"]
                t["pos"]         = p["pos"]
                t["team"]        = p["team"]
                t["flag"]        = p.get("flag", "")
        return trades
    except:
        return []

def get_leaderboard() -> list:
    sb = get_client()
    try:
        users = sb.table("users").select("username,cash").execute().data or []
        result = []
        for u in users:
            holdings = sb.table("portfolios").select("shares,player_id").eq("username", u["username"]).gt("shares", 0).execute().data or []
            hval = 0.0
            for h in holdings:
                p = get_player(h["player_id"])
                if p:
                    hval += h["shares"] * p["live_price"]
            total = u["cash"] + hval
            roi   = ((total - 700_000_000) / 700_000_000) * 100
            result.append({
                "username": u["username"], "cash": u["cash"],
                "holdings_value": hval, "total_value": total, "roi_pct": roi
            })
        return sorted(result, key=lambda x: x["roi_pct"], reverse=True)
    except Exception as e:
        print(f"[DB] Leaderboard error: {e}")
        return []

def get_conn():
    """Legacy compatibility — no longer used."""
    return None
