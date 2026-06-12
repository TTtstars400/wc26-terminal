import os
"""
api_client.py — Big Balls Data integration for WC26 Equity Terminal
--------------------------------------------------------------------
API: https://api.bigballsdata.com
Docs: https://bigballsdata.com/docs/introduction

Free tier: 1,000 requests/day — plenty for the World Cup.

What we get from Big Balls Data:
  ✅ Match results (score, winner, stage)
  ✅ Goal scorers
  ✅ Assists
  ✅ Yellow cards
  ✅ Red cards
  ✅ Own goals
  ✅ Penalty misses
  ✅ xG (match level)
  ✅ Possession / passes (match level)
  ✅ Lineups + minutes played
  ✅ Player club-form ratings

What we estimate automatically:
  ⚡ Pass accuracy (from team possession + position)
  ⚡ Progressive passes (from position + minutes)
  ⚡ Interceptions (from position + result)
  ⚡ Tackles won (from position + clean sheet)
  ⚡ Key passes (from ATT xG vs goals)
  ⚡ Dispossessed (low random probability)
  ⚡ Error to goal (very low random probability)
  ⚡ Big chance missed (from xG vs goals for ATTs)

Manual overrides available in Admin Panel for anything unusual.
"""

import requests
import time
import threading
import random
from datetime import datetime, timezone

import database as db
import valuation as val
import config

# ── Constants ─────────────────────────────────────────────────────────────────
BBS_BASE    = "https://api.bigballsdata.com/v1"
BBS_HEADERS = lambda key: {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}

# World Cup 2026 league key on Big Balls Data
WC_LEAGUE_KEY = "wc2026"

_scheduler_running = False
_scheduler_thread  = None


# ── Safe API caller ───────────────────────────────────────────────────────────
def _get(endpoint: str, params: dict = None, key: str = None) -> dict | None:
    """
    Safe API call with automatic throttling.
    Reads X-RateLimit headers to avoid ever hitting the limit.
    """
    api_key = key or os.environ.get("BBS_API_KEY", config.BBS_API_KEY)
    if not api_key or api_key in ("YOUR_BBS_KEY_HERE", ""):
        print("[BBS] No API key configured")
        return None

    try:
        r = requests.get(
            f"{BBS_BASE}{endpoint}",
            headers=BBS_HEADERS(api_key),
            params=params or {},
            timeout=15,
        )

        # Read rate limit headers
        remaining = int(r.headers.get("X-RateLimit-Remaining", 100))
        reset_in  = int(r.headers.get("X-RateLimit-Reset", 60))

        print(f"[BBS] {endpoint} → {r.status_code} | "
              f"Remaining: {remaining}/day | Reset: {reset_in}s")

        # Getting low — wait before next call
        if remaining <= 5:
            print(f"[BBS] ⚠ Only {remaining} calls left today — pausing {reset_in}s")
            time.sleep(min(reset_in, 300))

        if r.status_code == 429:
            retry = int(r.headers.get("Retry-After", 60))
            print(f"[BBS] 🔴 Rate limited — waiting {retry}s")
            time.sleep(retry)
            return _get(endpoint, params, key)

        if r.status_code == 404:
            print(f"[BBS] 404 — data not available for {endpoint}")
            return None

        r.raise_for_status()
        data = r.json()
        return data.get("data", data)

    except requests.exceptions.Timeout:
        print(f"[BBS] Timeout on {endpoint}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"[BBS] Connection error — check internet")
        return None
    except Exception as e:
        print(f"[BBS] Error {endpoint}: {e}")
        return None


# ── Schedule fetching ─────────────────────────────────────────────────────────
def fetch_schedule() -> int:
    """Fetch all 104 World Cup fixtures and store in DB."""
    data = _get("/matches", {"sport": "football", "league": WC_LEAGUE_KEY, "limit": 120})
    if not data:
        return 0

    matches = data if isinstance(data, list) else data.get("matches", [])
    count = 0
    for m in matches:
        try:
            # Parse scores
            scores = m.get("scores", {}).get("value", {}) or {}
            hs = scores.get("home")
            as_ = scores.get("away")

            # Map status
            raw_status = m.get("status", "").upper()
            status_map = {
                "NS": "SCHEDULED", "TBD": "TIMED",
                "1H": "IN_PLAY", "2H": "IN_PLAY",
                "HT": "PAUSED", "ET": "IN_PLAY",
                "FT": "FINISHED", "AET": "FINISHED",
                "PEN": "FINISHED", "AWD": "AWARDED",
            }
            status = status_map.get(raw_status, raw_status)

            db.upsert_match(
                api_fixture_id = m.get("id") or m.get("match_id"),
                home_team      = m.get("home", {}).get("name", ""),
                home_code      = m.get("home", {}).get("code", "")[:3].upper(),
                away_team      = m.get("away", {}).get("name", ""),
                away_code      = m.get("away", {}).get("code", "")[:3].upper(),
                kickoff_utc    = m.get("date") or m.get("kickoff") or "",
                stage          = m.get("stage") or m.get("round") or "GROUP_STAGE",
                status         = status,
                home_score     = hs,
                away_score     = as_,
            )
            count += 1
        except Exception as e:
            print(f"[BBS] Schedule store error: {e} — {m}")

    print(f"[BBS] Stored {count} fixtures")
    return count


# ── Status monitoring ─────────────────────────────────────────────────────────
def update_match_statuses():
    """Check for live and finished matches. Lock/unlock trading accordingly."""
    # Check live first
    live_data = _get("/matches", {
        "sport": "football", "league": WC_LEAGUE_KEY, "status": "live"
    })
    time.sleep(2)  # small gap between calls

    # Then check recently finished
    finished_data = _get("/matches", {
        "sport": "football", "league": WC_LEAGUE_KEY, "status": "finished", "limit": 10
    })

    all_matches = []
    if live_data:
        all_matches += live_data if isinstance(live_data, list) else []
    if finished_data:
        all_matches += finished_data if isinstance(finished_data, list) else []

    for m in all_matches:
        raw_status = m.get("status", "").upper()
        status_map = {
            "1H":"IN_PLAY","2H":"IN_PLAY","HT":"PAUSED","ET":"IN_PLAY",
            "FT":"FINISHED","AET":"FINISHED","PEN":"FINISHED","AWD":"AWARDED",
        }
        status    = status_map.get(raw_status, raw_status)
        fid       = m.get("id") or m.get("match_id")
        scores    = m.get("scores", {}).get("value", {}) or {}
        hs        = scores.get("home")
        as_       = scores.get("away")
        home_code = m.get("home", {}).get("code", "")[:3].upper()
        away_code = m.get("away", {}).get("code", "")[:3].upper()

        db.upsert_match(
            api_fixture_id=fid,
            home_team=m.get("home", {}).get("name", ""),
            home_code=home_code,
            away_team=m.get("away", {}).get("name", ""),
            away_code=away_code,
            kickoff_utc=m.get("date") or m.get("kickoff") or "",
            stage=m.get("stage") or "GROUP_STAGE",
            status=status,
            home_score=hs,
            away_score=as_,
        )

        if status in ("IN_PLAY", "PAUSED"):
            conn = db.get_conn()
            row = conn.execute(
                "SELECT id FROM matches WHERE api_fixture_id=?", (fid,)
            ).fetchone()
            conn.close()
            if row:
                db.lock_teams(row["id"], home_code, away_code)
                print(f"[BBS] 🔒 Locked: {home_code} vs {away_code}")


# ── Post-match processing ─────────────────────────────────────────────────────
def process_finished_matches() -> list:
    """Find finished unprocessed matches and update all player prices."""
    unprocessed = db.get_finished_unprocessed()
    if not unprocessed:
        return []

    all_results = []
    for match in unprocessed:
        print(f"[BBS] Processing: {match['home_team']} vs {match['away_team']}")
        try:
            results = _process_single_match(match)
            all_results.extend(results)
            db.unlock_teams(match["home_team_code"], match["away_team_code"])
            print(f"[BBS] 🔓 Unlocked: {match['home_team_code']} vs {match['away_team_code']}")
        except Exception as e:
            print(f"[BBS] Processing error: {e}")
        time.sleep(8)  # respect rate limits between matches

    return all_results


def _process_single_match(match: dict) -> list:
    """
    Fetch full stats for one match from Big Balls Data.
    Falls back gracefully if any endpoint is unavailable.
    """
    fid      = match.get("api_fixture_id")
    match_id = match["id"]
    hs  = match.get("home_score") or 0
    as_ = match.get("away_score") or 0
    home_won    = hs > as_
    away_won    = as_ > hs
    is_knockout = match.get("stage", "") not in ("GROUP_STAGE", "group_stage", "Group Stage", "")

    home_code = match["home_team_code"]
    away_code = match["away_team_code"]

    # ── Step 1: Fetch match events (goals, assists, cards) ────────────────────
    events_raw = []
    if fid:
        ev_data = _get(f"/matches/{fid}/events")
        time.sleep(2)
        if ev_data:
            events_raw = ev_data if isinstance(ev_data, list) else ev_data.get("events", [])

    # ── Step 2: Fetch match stats (xG, possession, passes) ───────────────────
    match_stats = {}
    if fid:
        stats_data = _get(f"/stored/matches/{fid}/stats")
        time.sleep(2)
        if stats_data:
            match_stats = stats_data if isinstance(stats_data, dict) else {}

    # ── Step 3: Fetch lineups (minutes played) ────────────────────────────────
    lineups_raw = {}
    if fid:
        lineup_data = _get(f"/stored/matches/{fid}/lineups")
        time.sleep(2)
        if lineup_data:
            lineups_raw = lineup_data if isinstance(lineup_data, dict) else {}

    # ── Step 4: Parse events into per-player dicts ────────────────────────────
    goals_by    = {}   # player_name_lower → int (count), -99 = own goal
    assists_by  = {}   # player_name_lower → int
    yellows_by  = {}   # player_name_lower → int
    reds_by     = {}   # player_name_lower → int
    own_goals_by = {}  # player_name_lower → int
    pen_miss_by = {}   # player_name_lower → int

    for ev in events_raw:
        etype   = str(ev.get("type", "") or ev.get("event_type", "")).lower()
        detail  = str(ev.get("detail", "") or ev.get("subtype", "")).lower()
        pname   = str(ev.get("player", "") or ev.get("player_name", "") or
                      (ev.get("player", {}) or {}).get("name", "")).lower().strip()
        aname   = str(ev.get("assist", "") or ev.get("assist_name", "") or
                      (ev.get("assist", {}) or {}).get("name", "")).lower().strip()

        if "goal" in etype:
            if "own" in etype or "own" in detail:
                own_goals_by[pname] = own_goals_by.get(pname, 0) + 1
            elif "missed" in detail or "penalty" in detail and "miss" in detail:
                pen_miss_by[pname] = pen_miss_by.get(pname, 0) + 1
            else:
                goals_by[pname] = goals_by.get(pname, 0) + 1
            if aname and aname != pname:
                assists_by[aname] = assists_by.get(aname, 0) + 1

        elif "card" in etype or "yellow" in etype:
            if "red" in etype or "red" in detail:
                reds_by[pname] = reds_by.get(pname, 0) + 1
            else:
                yellows_by[pname] = yellows_by.get(pname, 0) + 1

    # ── Step 5: Parse match-level stats ───────────────────────────────────────
    home_stats = {}
    away_stats = {}
    if match_stats:
        # Try various response shapes from different API sources
        if "home" in match_stats and "away" in match_stats:
            home_stats = match_stats.get("home") or {}
            away_stats = match_stats.get("away") or {}
        elif isinstance(match_stats, list) and len(match_stats) >= 2:
            home_stats = match_stats[0]
            away_stats = match_stats[1]

    def _stat(team_stats, *keys, default=0.0):
        """Safely extract a stat trying multiple key names."""
        for k in keys:
            v = team_stats.get(k)
            if v is not None:
                try: return float(v)
                except: pass
        return default

    home_xg         = _stat(home_stats, "xg", "expected_goals", "xG")
    away_xg         = _stat(away_stats, "xg", "expected_goals", "xG")
    home_possession = _stat(home_stats, "possession", "ball_possession")
    away_possession = _stat(away_stats, "possession", "ball_possession")
    home_passes     = _stat(home_stats, "passes", "total_passes")
    away_passes     = _stat(away_stats, "passes", "total_passes")
    home_pass_acc   = _stat(home_stats, "pass_accuracy", "passes_accuracy", "passes_percentage")
    away_pass_acc   = _stat(away_stats, "pass_accuracy", "passes_accuracy", "passes_percentage")

    # ── Step 6: Parse lineups for minutes ─────────────────────────────────────
    minutes_by = {}  # player_name_lower → minutes played
    for side in ["home", "away"]:
        side_lineup = lineups_raw.get(side, {})
        if isinstance(side_lineup, dict):
            players = side_lineup.get("startXI", []) + side_lineup.get("substitutes", [])
        elif isinstance(side_lineup, list):
            players = side_lineup
        else:
            players = []
        for pl in players:
            if isinstance(pl, dict):
                pname = str(pl.get("name", "") or pl.get("player", {}).get("name", "")).lower()
                mins  = pl.get("minutes", 90) or 90
                if pname:
                    minutes_by[pname] = int(mins)

    # ── Step 7: Build PlayerMatchStats for each of our players ───────────────
    all_stats = []

    for team_code, team_won, goals_for, goals_against, t_xg, t_possession, t_pass_acc in [
        (home_code, home_won, hs, as_, home_xg, home_possession, home_pass_acc),
        (away_code, away_won, as_, hs,  away_xg, away_possession, away_pass_acc),
    ]:
        clean_sheet = goals_against == 0
        our_players = db.get_players_by_team(team_code)

        for player in our_players:
            pos   = player["pos"]
            pname = player["name"].lower()

            # Match player name to event data (fuzzy)
            g_key  = _fuzzy_match(pname, list(goals_by.keys()))
            a_key  = _fuzzy_match(pname, list(assists_by.keys()))
            y_key  = _fuzzy_match(pname, list(yellows_by.keys()))
            r_key  = _fuzzy_match(pname, list(reds_by.keys()))
            og_key = _fuzzy_match(pname, list(own_goals_by.keys()))
            pm_key = _fuzzy_match(pname, list(pen_miss_by.keys()))
            m_key  = _fuzzy_match(pname, list(minutes_by.keys()))

            goals     = goals_by.get(g_key, 0) if g_key else 0
            assists   = assists_by.get(a_key, 0) if a_key else 0
            yellows   = yellows_by.get(y_key, 0) if y_key else 0
            reds      = reds_by.get(r_key, 0) if r_key else 0
            own_goals = own_goals_by.get(og_key, 0) if og_key else 0
            pen_miss  = pen_miss_by.get(pm_key, 0) if pm_key else 0
            minutes   = minutes_by.get(m_key, 90) if m_key else 90

            stats = val.PlayerMatchStats(
                player_id    = player["id"],
                minutes_played = minutes,
                goals        = goals,
                assists      = assists,
                own_goals    = own_goals,
                penalty_misses = pen_miss,
                yellow_cards = yellows,
                red_cards    = reds,
                team_won     = team_won,
                team_eliminated = is_knockout and not team_won and hs != as_,
            )

            # ── Position-specific estimated stats ─────────────────────────────
            if pos == "ATT":
                # xG outperformed: scored more than xG suggested
                if t_xg > 0 and goals > 0:
                    stats.xg_outperformed = goals >= t_xg
                # Key passes: estimated from ATT role + minutes
                stats.key_passes = max(0, int(random.gauss(1.2, 0.8))) if minutes >= 60 else 0
                # Big chance missed: if low xG but no goals
                stats.big_chances_missed = (
                    random.randint(0, 1)
                    if t_xg > 0.5 and goals == 0 and minutes >= 60
                    else 0
                )

            elif pos == "MID":
                # Pass accuracy: use real team data if available, else estimate
                if t_pass_acc > 0:
                    # Individual accuracy varies ±5% around team average
                    stats.pass_accuracy = max(50, min(99,
                        t_pass_acc + random.uniform(-5, 5)))
                elif t_possession > 0:
                    # Estimate from possession: high possession = high pass acc
                    stats.pass_accuracy = max(65, min(96,
                        60 + (t_possession * 0.6) + random.uniform(-3, 3)))
                else:
                    stats.pass_accuracy = random.gauss(83, 6)

                # Progressive passes: estimated
                stats.progressive_passes = (
                    max(0, int(random.gauss(2.5, 1.2))) if minutes >= 60 else 0
                )
                # Interceptions
                stats.interceptions = (
                    max(0, int(random.gauss(1.5, 1.0))) if minutes >= 60 else 0
                )
                # Dispossessed: low probability
                stats.times_dispossessed = (
                    1 if random.random() < 0.15 else 0
                )

            elif pos in ("DEF", "GK"):
                stats.clean_sheet    = clean_sheet and minutes >= 60
                stats.goals_conceded = goals_against

                if pos == "GK":
                    # Saves: goals conceded + blocked shots
                    stats.saves = max(0, goals_against + random.randint(0, 5))
                else:
                    # Tackles: estimated from DEF role
                    stats.tackles_won = max(0, int(random.gauss(2.5, 1.2)))
                    # Error to goal: very rare
                    stats.errors_to_goal = (
                        1 if random.random() < 0.04 and goals_against > 0 else 0
                    )

            # ── Match rating: derived from real events + estimates ─────────────
            stats.match_rating = _derive_rating(stats, pos, team_won, minutes)

            all_stats.append(stats)

    return val.process_full_match(match_id, all_stats)


# ── Manual match processing (Admin Panel) ─────────────────────────────────────
def process_manual_match(match_id: int, home_code: str, away_code: str,
                         home_goals: int, away_goals: int,
                         is_knockout: bool = False,
                         manual_events: list = None) -> list:
    """
    Process a manually entered match result.
    manual_events: optional list of dicts:
      [{"player_id": "MBP", "event_type": "GOAL", "description": "67' volley"}, ...]
    """
    match = {
        "id": match_id,
        "home_team_code": home_code,
        "away_team_code": away_code,
        "home_score": home_goals,
        "away_score": away_goals,
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
            pos = player["pos"]
            stats = val.PlayerMatchStats(
                player_id      = player["id"],
                minutes_played = 90,
                team_won       = team_won,
                team_eliminated = is_knockout and not team_won and home_goals != away_goals,
            )

            # Apply manual events if provided
            if manual_events:
                for ev in manual_events:
                    if ev.get("player_id") == player["id"]:
                        etype = ev.get("event_type", "")
                        if etype == "GOAL":          stats.goals += 1
                        elif etype == "ASSIST":      stats.assists += 1
                        elif etype == "YELLOW_CARD": stats.yellow_cards += 1
                        elif etype == "RED_CARD":    stats.red_cards += 1
                        elif etype == "OWN_GOAL":    stats.own_goals += 1
                        elif etype == "PENALTY_MISS": stats.penalty_misses += 1
                        elif etype == "SAVE":        stats.saves += 1

            # Fill in estimated stats by position
            if pos in ("DEF", "GK"):
                stats.clean_sheet    = clean
                stats.goals_conceded = goals_against
                if pos == "GK" and stats.saves == 0:
                    stats.saves = max(0, goals_against + random.randint(0, 4))
                if pos == "DEF" and stats.tackles_won == 0:
                    stats.tackles_won = max(0, int(random.gauss(2, 1)))
            elif pos == "MID":
                if stats.pass_accuracy == 0:
                    stats.pass_accuracy = random.gauss(83, 6)
                if stats.progressive_passes == 0:
                    stats.progressive_passes = max(0, int(random.gauss(2, 1)))
                if stats.interceptions == 0:
                    stats.interceptions = max(0, int(random.gauss(1.5, 1)))
            elif pos == "ATT":
                if stats.key_passes == 0:
                    stats.key_passes = max(0, int(random.gauss(1, 0.8)))

            stats.match_rating = _derive_rating(stats, pos, team_won, 90)
            all_stats.append(stats)

    results = val.process_full_match(match_id, all_stats)
    db.unlock_teams(home_code, away_code)
    return results


# ── Apply a single manual event to one player ─────────────────────────────────
def apply_single_manual_event(player_id: str, event_type: str,
                               custom_pct: float = None,
                               description: str = "") -> val.PlayerPriceResult | None:
    """
    Manually apply one event to one player right now.
    Used from Admin Panel for corrections or unusual situations.
    custom_pct: if set, overrides the standard % for this event type.
    """
    player = db.get_player(player_id)
    if not player:
        return None

    # Build a minimal stats object with just this one event
    stats = val.PlayerMatchStats(
        player_id      = player_id,
        minutes_played = 90,
    )

    pos = player["pos"]

    # Apply the specific event
    event_map = {
        "GOAL":             lambda s: setattr(s, "goals", s.goals + 1),
        "ASSIST":           lambda s: setattr(s, "assists", s.assists + 1),
        "YELLOW_CARD":      lambda s: setattr(s, "yellow_cards", s.yellow_cards + 1),
        "RED_CARD":         lambda s: setattr(s, "red_cards", s.red_cards + 1),
        "OWN_GOAL":         lambda s: setattr(s, "own_goals", s.own_goals + 1),
        "PENALTY_MISS":     lambda s: setattr(s, "penalty_misses", s.penalty_misses + 1),
        "CLEAN_SHEET":      lambda s: setattr(s, "clean_sheet", True),
        "SAVE":             lambda s: setattr(s, "saves", s.saves + 1),
        "TACKLE":           lambda s: setattr(s, "tackles_won", s.tackles_won + 1),
        "GOAL_CONCEDED":    lambda s: setattr(s, "goals_conceded", s.goals_conceded + 1),
        "ERROR_TO_GOAL":    lambda s: setattr(s, "errors_to_goal", s.errors_to_goal + 1),
        "TEAM_WIN":         lambda s: setattr(s, "team_won", True),
        "TEAM_ADVANCE":     lambda s: setattr(s, "team_advanced", True),
        "TEAM_ELIMINATED":  lambda s: setattr(s, "team_eliminated", True),
        "PASS_ACC_90":      lambda s: setattr(s, "pass_accuracy", 92.0),
        "BIG_CHANCE_MISSED": lambda s: setattr(s, "big_chances_missed", s.big_chances_missed + 1),
    }

    if event_type in event_map:
        event_map[event_type](stats)

    # If custom_pct override, apply directly to price
    if custom_pct is not None:
        old_price = player["live_price"]
        new_price = max(0.50, round(old_price * (1 + custom_pct / 100), 4))
        db.update_player_price(
            player_id, new_price,
            reason=f"MANUAL:{event_type}({custom_pct:+.1f}%)",
        )
        db.log_match_event(None, player_id, f"MANUAL_{event_type}",
                           custom_pct, description or f"Manual: {event_type}")
        return val.PlayerPriceResult(
            player_id=player_id, player_name=player["name"],
            pos=pos, flag=player.get("flag", ""), team=player["team"],
            old_price=old_price, new_price=new_price,
            total_delta_pct=custom_pct,
        )

    return val.apply_player_stats(stats)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _fuzzy_match(target: str, candidates: list[str]) -> str | None:
    """
    Match a player name from our DB to a name from the API events.
    Tries surname match first, then partial.
    """
    if not target or not candidates:
        return None

    target_parts = [p for p in target.split() if len(p) > 2]

    # Exact match first
    if target in candidates:
        return target

    # Surname match (last word of name)
    if target_parts:
        surname = target_parts[-1]
        for c in candidates:
            if surname in c or c in target:
                return c

    # Any part match
    for part in target_parts:
        for c in candidates:
            if part in c:
                return c

    return None


def _derive_rating(stats: val.PlayerMatchStats, pos: str,
                   team_won: bool, minutes: int) -> float:
    """
    Derive a realistic 0-10 match rating from available stats.
    Uses real event data where available, estimates the rest.
    """
    base = 6.8 if team_won else 6.1

    if pos == "ATT":
        base += stats.goals * 0.9
        base += stats.assists * 0.6
        base -= stats.big_chances_missed * 0.5
        base -= stats.penalty_misses * 0.8
        base -= stats.yellow_cards * 0.3
        base -= stats.red_cards * 2.0
        if stats.xg_outperformed: base += 0.3

    elif pos == "MID":
        if stats.pass_accuracy >= 90: base += 0.5
        elif stats.pass_accuracy >= 85: base += 0.2
        base += min(stats.interceptions * 0.25, 0.6)
        base += min(stats.progressive_passes * 0.15, 0.4)
        base -= stats.times_dispossessed * 0.25
        base -= stats.yellow_cards * 0.35
        base -= stats.red_cards * 2.0

    elif pos in ("DEF", "GK"):
        if stats.clean_sheet and minutes >= 60: base += 0.9
        if pos == "GK":
            base += min(stats.saves * 0.25, 1.2)
        else:
            base += min(stats.tackles_won * 0.18, 0.7)
        base -= stats.goals_conceded * 0.35
        base -= stats.errors_to_goal * 1.0
        base -= stats.own_goals * 1.2
        base -= stats.yellow_cards * 0.35
        base -= stats.red_cards * 2.0

    # Minutes penalty for subs
    if minutes < 45: base -= 0.5
    elif minutes < 60: base -= 0.2

    # Small random variation ±0.3
    base += random.uniform(-0.3, 0.3)

    return max(3.0, min(10.0, round(base, 1)))


# ── Scheduler ─────────────────────────────────────────────────────────────────
def start_scheduler():
    global _scheduler_running, _scheduler_thread
    if _scheduler_running:
        return
    _scheduler_running = True

    def _loop():
        last_schedule_fetch = 0
        schedule_interval   = 6 * 3600  # refresh schedule every 6 hours
        first_run           = True       # fetch immediately on startup

        while _scheduler_running:
            try:
                api_ready = bool(os.environ.get("BBS_API_KEY", "").strip())

                if api_ready:
                    now = time.time()

                    # Fetch schedule immediately on first run OR every 6 hours
                    if first_run or (now - last_schedule_fetch > schedule_interval):
                        print("[Scheduler] Fetching WC2026 schedule...")
                        count = fetch_schedule()
                        print(f"[Scheduler] Schedule: {count} fixtures loaded")
                        last_schedule_fetch = now
                        first_run = False
                        time.sleep(3)

                    # Check match statuses and lock/unlock trading
                    update_match_statuses()
                    time.sleep(3)

                    # Process any finished matches and update prices
                    results = process_finished_matches()
                    if results:
                        print(f"[Scheduler] ✅ {len(results)} player price updates applied")

                else:
                    print("[Scheduler] No API key found in environment variables.")
                    first_run = True  # retry fetch when key becomes available

            except Exception as e:
                print(f"[Scheduler] Error: {e}")

            time.sleep(config.MATCH_POLL_INTERVAL)

    _scheduler_thread = threading.Thread(target=_loop, daemon=True)
    _scheduler_thread.start()
    print(f"[Scheduler] Started — polling every {config.MATCH_POLL_INTERVAL}s")


def stop_scheduler():
    global _scheduler_running
    _scheduler_running = False
    print("[Scheduler] Stopped.")


def is_running() -> bool:
    return _scheduler_running
