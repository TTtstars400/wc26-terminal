"""
api_client.py - football-data.org integration for WC26 Equity Terminal
Free tier: 10 calls/minute, no card needed
Covers: match results, scorers, cards, stage advancement
"""

import requests
import time
import threading
import random
import os
from datetime import datetime, timezone

import database as db
import valuation as val
import config

FD_BASE    = "https://api.football-data.org/v4"
WC_ID      = 2000  # FIFA World Cup ID on football-data.org

_scheduler_running = False
_scheduler_thread  = None


def _get_fd(endpoint, params=None):
    """Call football-data.org with rate limit handling."""
    key = os.environ.get("FOOTBALL_DATA_API_KEY", config.FOOTBALL_DATA_API_KEY)
    if not key or key == "":
        print("[FD] No football-data.org key found")
        return None
    try:
        r = requests.get(
            f"{FD_BASE}{endpoint}",
            headers={"X-Auth-Token": key},
            params=params or {},
            timeout=15
        )
        remaining = int(r.headers.get("X-Requests-Available-Minute", 10))
        print(f"[FD] {endpoint} -> {r.status_code} | Remaining: {remaining}/min")

        if remaining <= 2:
            print("[FD] Near rate limit — waiting 65s")
            time.sleep(65)

        if r.status_code == 429:
            wait = int(r.headers.get("Retry-After", 65))
            print(f"[FD] Rate limited — waiting {wait}s")
            time.sleep(wait)
            return _get_fd(endpoint, params)

        if r.status_code == 403:
            print(f"[FD] 403 Forbidden — check API key or plan limits")
            return None

        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        print(f"[FD] Timeout on {endpoint}")
        return None
    except Exception as e:
        print(f"[FD] Error {endpoint}: {e}")
        return None


def fetch_schedule() -> int:
    """Fetch all WC2026 fixtures from football-data.org."""
    data = _get_fd(f"/competitions/{WC_ID}/matches")
    if not data:
        return 0

    matches = data.get("matches", [])
    count = 0
    for m in matches:
        try:
            score = m.get("score", {})
            ft    = score.get("fullTime", {})
            hs    = ft.get("home")
            as_   = ft.get("away")

            status_map = {
                "SCHEDULED": "SCHEDULED", "TIMED": "TIMED",
                "IN_PLAY": "IN_PLAY", "PAUSED": "PAUSED",
                "FINISHED": "FINISHED", "AWARDED": "AWARDED",
                "CANCELLED": "CANCELLED", "POSTPONED": "POSTPONED",
            }
            status = status_map.get(m.get("status", ""), "SCHEDULED")

            home = m.get("homeTeam", {})
            away = m.get("awayTeam", {})

            db.upsert_match(
                api_fixture_id = m["id"],
                home_team      = home.get("name", ""),
                home_code      = home.get("tla", home.get("name","")[:3].upper()),
                away_team      = away.get("name", ""),
                away_code      = away.get("tla", away.get("name","")[:3].upper()),
                kickoff_utc    = m.get("utcDate", ""),
                stage          = m.get("stage", "GROUP_STAGE"),
                status         = status,
                home_score     = hs,
                away_score     = as_,
            )
            count += 1
        except Exception as e:
            print(f"[FD] Match store error: {e}")

    print(f"[FD] Stored {count} fixtures")
    return count


def update_match_statuses():
    """Check for live and recently finished matches."""
    for status_filter in ["LIVE", "IN_PLAY"]:
        data = _get_fd(f"/competitions/{WC_ID}/matches",
                       {"status": status_filter})
        if not data:
            continue
        for m in data.get("matches", []):
            _update_single_match_status(m, lock=True)
        time.sleep(6)

    # Check finished matches too
    data = _get_fd(f"/competitions/{WC_ID}/matches",
                   {"status": "FINISHED"})
    if data:
        for m in data.get("matches", []):
            _update_single_match_status(m, lock=False)


def _update_single_match_status(m, lock=False):
    fid       = m["id"]
    status    = m.get("status", "")
    home      = m.get("homeTeam", {})
    away      = m.get("awayTeam", {})
    home_code = home.get("tla", "")
    away_code = away.get("tla", "")
    ft        = m.get("score", {}).get("fullTime", {})

    db.upsert_match(
        api_fixture_id = fid,
        home_team      = home.get("name", ""),
        home_code      = home_code,
        away_team      = away.get("name", ""),
        away_code      = away_code,
        kickoff_utc    = m.get("utcDate", ""),
        stage          = m.get("stage", "GROUP_STAGE"),
        status         = status,
        home_score     = ft.get("home"),
        away_score     = ft.get("away"),
    )

    if lock and status in ("IN_PLAY", "PAUSED"):
        conn = db.get_conn()
        if conn is None:
            sb = db.get_client()
            row = sb.table("matches").select("id").eq("api_fixture_id", fid).execute()
            if row.data:
                db.lock_teams(row.data[0]["id"], home_code, away_code)
        else:
            row = conn.execute("SELECT id FROM matches WHERE api_fixture_id=?", (fid,)).fetchone()
            if row:
                db.lock_teams(row["id"], home_code, away_code)
        print(f"[FD] Locked: {home_code} vs {away_code}")


def process_finished_matches() -> list:
    """Process all unprocessed finished matches."""
    unprocessed = db.get_finished_unprocessed()
    if not unprocessed:
        return []

    all_results = []
    for match in unprocessed:
        print(f"[FD] Processing: {match['home_team']} vs {match['away_team']}")
        try:
            results = _process_single_match(match)
            all_results.extend(results)
            db.unlock_teams(match["home_team_code"], match["away_team_code"])
            print(f"[FD] Unlocked: {match['home_team_code']} vs {match['away_team_code']}")
        except Exception as e:
            print(f"[FD] Processing error: {e}")
        time.sleep(7)

    return all_results


def _process_single_match(match: dict) -> list:
    fid      = match.get("api_fixture_id")
    match_id = match["id"]
    hs       = match.get("home_score") or 0
    as_      = match.get("away_score") or 0
    home_won = hs > as_
    away_won = as_ > hs
    is_ko    = match.get("stage", "") not in (
        "GROUP_STAGE", "group_stage", "Group Stage", ""
    )

    home_code = match["home_team_code"]
    away_code = match["away_team_code"]

    # Fetch match events (goals, cards) from football-data.org
    goals_by    = {}
    assists_by  = {}
    yellows_by  = {}
    reds_by     = {}
    own_goals_by= {}
    pen_miss_by = {}

    if fid:
        match_data = _get_fd(f"/matches/{fid}")
        time.sleep(6)
        if match_data:
            for goal in match_data.get("goals", []):
                scorer = (goal.get("scorer") or {}).get("name", "").lower()
                assist = (goal.get("assist") or {})
                aname  = assist.get("name", "").lower() if assist else ""
                gtype  = goal.get("type", "REGULAR")
                if gtype == "OWN_GOAL":
                    own_goals_by[scorer] = own_goals_by.get(scorer, 0) + 1
                elif gtype == "MISSED_PENALTY":
                    pen_miss_by[scorer] = pen_miss_by.get(scorer, 0) + 1
                else:
                    goals_by[scorer] = goals_by.get(scorer, 0) + 1
                    if aname:
                        assists_by[aname] = assists_by.get(aname, 0) + 1

            for booking in match_data.get("bookings", []):
                pname = (booking.get("player") or {}).get("name", "").lower()
                card  = booking.get("card", "YELLOW_CARD")
                if "RED" in card.upper():
                    reds_by[pname] = reds_by.get(pname, 0) + 1
                else:
                    yellows_by[pname] = yellows_by.get(pname, 0) + 1

    # Build stats for all our players in both teams
    all_stats = []
    for team_code, team_won, goals_for, goals_against in [
        (home_code, home_won, hs, as_),
        (away_code, away_won, as_, hs),
    ]:
        clean = goals_against == 0
        for player in db.get_players_by_team(team_code):
            pos   = player["pos"]
            pname = player["name"].lower()

            g_key  = _fuzzy(pname, list(goals_by.keys()))
            a_key  = _fuzzy(pname, list(assists_by.keys()))
            y_key  = _fuzzy(pname, list(yellows_by.keys()))
            r_key  = _fuzzy(pname, list(reds_by.keys()))
            og_key = _fuzzy(pname, list(own_goals_by.keys()))
            pm_key = _fuzzy(pname, list(pen_miss_by.keys()))

            stats = val.PlayerMatchStats(
                player_id      = player["id"],
                minutes_played = 90,
                goals          = goals_by.get(g_key, 0) if g_key else 0,
                assists        = assists_by.get(a_key, 0) if a_key else 0,
                own_goals      = own_goals_by.get(og_key, 0) if og_key else 0,
                penalty_misses = pen_miss_by.get(pm_key, 0) if pm_key else 0,
                yellow_cards   = yellows_by.get(y_key, 0) if y_key else 0,
                red_cards      = reds_by.get(r_key, 0) if r_key else 0,
                team_won       = team_won,
                team_eliminated= is_ko and not team_won and hs != as_,
            )

            # Estimate position-specific stats
            if pos in ("DEF", "GK"):
                stats.clean_sheet    = clean
                stats.goals_conceded = goals_against
                if pos == "GK":
                    stats.saves = max(0, goals_against + random.randint(0, 4))
                else:
                    stats.tackles_won = random.randint(1, 4)
                    stats.errors_to_goal = 1 if random.random() < 0.04 and goals_against > 0 else 0
            elif pos == "MID":
                stats.pass_accuracy      = random.gauss(83, 6)
                stats.progressive_passes = random.randint(2, 6)
                stats.interceptions      = random.randint(0, 3)
                stats.times_dispossessed = random.randint(0, 2)
            elif pos == "ATT":
                stats.xg_outperformed    = stats.goals > 0 and random.random() < 0.4
                stats.key_passes         = random.randint(0, 3)
                stats.big_chances_missed = random.randint(0,1) if stats.goals == 0 else 0

            stats.match_rating = _estimate_rating(stats, team_won)
            all_stats.append(stats)

    return val.process_full_match(match_id, all_stats)


def _fuzzy(target, candidates):
    if not target or not candidates: return None
    parts = [p for p in target.split() if len(p) > 2]
    if target in candidates: return target
    if parts:
        surname = parts[-1]
        for c in candidates:
            if surname in c or c in target or target in c:
                return c
    for part in parts:
        for c in candidates:
            if part in c: return c
    return None


def _estimate_rating(stats, team_won):
    base = 6.8 if team_won else 6.1
    base += stats.goals * 0.9 + stats.assists * 0.6
    base -= stats.own_goals * 1.2 + stats.errors_to_goal * 0.8
    base -= stats.red_cards * 1.5 + stats.yellow_cards * 0.2
    if stats.clean_sheet: base += 0.8
    if stats.pos if hasattr(stats, 'pos') else False: pass
    base += min(stats.saves * 0.2, 1.0)
    base += min(stats.tackles_won * 0.15, 0.6)
    base -= stats.goals_conceded * 0.3
    base -= stats.big_chances_missed * 0.4
    return max(3.0, min(10.0, round(base + random.uniform(-0.3, 0.3), 1)))


def process_manual_match(match_id, home_code, away_code,
                         home_goals, away_goals, is_knockout=False,
                         manual_events=None):
    match = {
        "id": match_id, "home_team_code": home_code, "away_team_code": away_code,
        "home_score": home_goals, "away_score": away_goals,
        "stage": "ROUND_OF_16" if is_knockout else "GROUP_STAGE",
        "api_fixture_id": None,
    }
    home_won = home_goals > away_goals
    away_won = away_goals > home_goals
    all_stats = []

    for team_code, team_won, goals_for, goals_against in [
        (home_code, home_won, home_goals, away_goals),
        (away_code, away_won, away_goals, home_goals),
    ]:
        clean = goals_against == 0
        for player in db.get_players_by_team(team_code):
            pos   = player["pos"]
            stats = val.PlayerMatchStats(
                player_id      = player["id"],
                minutes_played = 90,
                team_won       = team_won,
                team_eliminated= is_knockout and not team_won and home_goals != away_goals,
            )
            if manual_events:
                for ev in manual_events:
                    if ev.get("player_id") == player["id"]:
                        etype = ev.get("event_type","")
                        if etype == "GOAL":            stats.goals += 1
                        elif etype == "ASSIST":        stats.assists += 1
                        elif etype == "YELLOW_CARD":   stats.yellow_cards += 1
                        elif etype == "RED_CARD":      stats.red_cards += 1
                        elif etype == "OWN_GOAL":      stats.own_goals += 1
                        elif etype == "PENALTY_MISS":  stats.penalty_misses += 1
                        elif etype == "SAVE":          stats.saves += 1

            if pos in ("DEF", "GK"):
                stats.clean_sheet    = clean
                stats.goals_conceded = goals_against
                if pos == "GK" and stats.saves == 0:
                    stats.saves = max(0, goals_against + random.randint(0,4))
                if pos == "DEF" and stats.tackles_won == 0:
                    stats.tackles_won = max(0, int(random.gauss(2, 1)))
            elif pos == "MID":
                if stats.pass_accuracy == 0:
                    stats.pass_accuracy = random.gauss(83, 6)
                if stats.progressive_passes == 0:
                    stats.progressive_passes = random.randint(2, 5)
                if stats.interceptions == 0:
                    stats.interceptions = random.randint(0, 2)
            elif pos == "ATT":
                if stats.key_passes == 0:
                    stats.key_passes = random.randint(0, 2)

            stats.match_rating = _estimate_rating(stats, team_won)
            all_stats.append(stats)

    results = val.process_full_match(match_id, all_stats)
    db.unlock_teams(home_code, away_code)
    return results


def apply_single_manual_event(player_id, event_type,
                               custom_pct=None, description=""):
    player = db.get_player(player_id)
    if not player: return None

    stats = val.PlayerMatchStats(player_id=player_id, minutes_played=90)
    event_map = {
        "GOAL":            lambda s: setattr(s, "goals", s.goals+1),
        "ASSIST":          lambda s: setattr(s, "assists", s.assists+1),
        "YELLOW_CARD":     lambda s: setattr(s, "yellow_cards", s.yellow_cards+1),
        "RED_CARD":        lambda s: setattr(s, "red_cards", s.red_cards+1),
        "OWN_GOAL":        lambda s: setattr(s, "own_goals", s.own_goals+1),
        "PENALTY_MISS":    lambda s: setattr(s, "penalty_misses", s.penalty_misses+1),
        "CLEAN_SHEET":     lambda s: setattr(s, "clean_sheet", True),
        "SAVE":            lambda s: setattr(s, "saves", s.saves+1),
        "TACKLE":          lambda s: setattr(s, "tackles_won", s.tackles_won+1),
        "GOAL_CONCEDED":   lambda s: setattr(s, "goals_conceded", s.goals_conceded+1),
        "ERROR_TO_GOAL":   lambda s: setattr(s, "errors_to_goal", s.errors_to_goal+1),
        "TEAM_WIN":        lambda s: setattr(s, "team_won", True),
        "TEAM_ADVANCE":    lambda s: setattr(s, "team_advanced", True),
        "TEAM_ELIMINATED": lambda s: setattr(s, "team_eliminated", True),
        "PASS_ACC_90":     lambda s: setattr(s, "pass_accuracy", 92.0),
        "BIG_CHANCE_MISSED": lambda s: setattr(s, "big_chances_missed", s.big_chances_missed+1),
    }
    if event_type in event_map:
        event_map[event_type](stats)

    if custom_pct is not None:
        old_price = player["live_price"]
        new_price = max(0.50, round(old_price * (1 + custom_pct/100), 4))
        db.update_player_price(player_id, new_price,
                               reason=f"MANUAL:{event_type}({custom_pct:+.1f}%)")
        db.log_match_event(None, player_id, f"MANUAL_{event_type}",
                           custom_pct, description or f"Manual: {event_type}")
        return val.PlayerPriceResult(
            player_id=player_id, player_name=player["name"],
            pos=player["pos"], flag=player.get("flag",""), team=player["team"],
            old_price=old_price, new_price=new_price, total_delta_pct=custom_pct,
        )
    return val.apply_player_stats(stats)


def start_scheduler():
    global _scheduler_running, _scheduler_thread
    if _scheduler_running: return
    _scheduler_running = True

    def _loop():
        last_schedule_fetch = 0
        first_run = True
        while _scheduler_running:
            try:
                fd_key = os.environ.get("FOOTBALL_DATA_API_KEY", "")
                if fd_key:
                    now = time.time()
                    if first_run or (now - last_schedule_fetch > 6*3600):
                        count = fetch_schedule()
                        print(f"[Scheduler] Schedule: {count} fixtures")
                        last_schedule_fetch = now
                        first_run = False
                        time.sleep(7)
                    update_match_statuses()
                    time.sleep(7)
                    results = process_finished_matches()
                    if results:
                        print(f"[Scheduler] {len(results)} price updates")
                else:
                    print("[Scheduler] No FOOTBALL_DATA_API_KEY in environment")
                    first_run = True
            except Exception as e:
                print(f"[Scheduler] Error: {e}")
            time.sleep(config.MATCH_POLL_INTERVAL)

    _scheduler_thread = threading.Thread(target=_loop, daemon=True)
    _scheduler_thread.start()
    print(f"[Scheduler] Started")


def stop_scheduler():
    global _scheduler_running
    _scheduler_running = False


def is_running():
    return _scheduler_running
