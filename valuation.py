"""
valuation.py — Universal post-match price calculation engine
-------------------------------------------------------------
ALL events apply to ALL positions. No position restrictions.
Every player is rewarded or penalised based on what they actually did.

Progressive passes: +1% per pass, but only triggers at 2+ passes
                    (so 1 progressive pass = 0%, 2 = +1%, 3 = +1%, 4 = +2% etc)

Rating: 8.5+ -> +4% | 7.5+ -> +2% | 6.5+ -> 0% | 5.0+ -> -1% | below 5 -> -3%
"""

from dataclasses import dataclass, field
import database as db
import config


@dataclass
class PlayerMatchStats:
    player_id:          str
    minutes_played:     int   = 0
    goals:              int   = 0
    assists:            int   = 0
    xg_outperformed:    bool  = False
    key_passes:         int   = 0
    penalty_misses:     int   = 0
    big_chances_missed: int   = 0
    pass_accuracy:      float = 0.0
    progressive_passes: int   = 0
    interceptions:      int   = 0
    times_dispossessed: int   = 0
    yellow_cards:       int   = 0
    red_cards:          int   = 0
    clean_sheet:        bool  = False
    saves:              int   = 0
    tackles_won:        int   = 0
    goals_conceded:     int   = 0
    own_goals:          int   = 0
    errors_to_goal:     int   = 0
    team_won:           bool  = False
    team_advanced:      bool  = False
    team_eliminated:    bool  = False
    match_rating:       float | None = None


@dataclass
class PriceChange:
    event_type:  str
    delta_pct:   float
    description: str


@dataclass
class PlayerPriceResult:
    player_id:       str
    player_name:     str
    pos:             str
    flag:            str
    team:            str
    old_price:       float
    new_price:       float
    total_delta_pct: float
    changes:         list = field(default_factory=list)
    match_rating:    float | None = None


def rating_to_delta(rating):
    for threshold, delta in config.RATING_THRESHOLDS:
        if rating >= threshold:
            labels = {4.0:"Outstanding", 2.0:"Good", 0.0:"Average",
                      -1.0:"Below par", -3.0:"Poor"}
            return delta, f"Match rating {rating:.1f}/10 — {labels.get(delta,'')}"
    return -3.0, f"Match rating {rating:.1f}/10 — Poor"


def calculate_deltas(stats: PlayerMatchStats) -> list[PriceChange]:
    """
    Universal rules — apply to ALL players regardless of position.
    """
    changes = []

    def add(event, delta, desc):
        changes.append(PriceChange(event, delta, desc))

    # ── Goals & Attacking ─────────────────────────────────────────────────────
    for _ in range(stats.goals):
        add("GOAL", +5.0, "⚽ Goal scored (+5%)")
    for _ in range(stats.assists):
        add("ASSIST", +3.0, "🎯 Assist (+3%)")
    if stats.xg_outperformed:
        add("XG_OUT", +2.0, "📊 xG outperformed (+2%)")
    for _ in range(stats.key_passes):
        add("KEY_PASS", +1.0, "🔑 Key pass (+1%)")
    for _ in range(stats.penalty_misses):
        add("PEN_MISS", -4.0, "❌ Penalty miss (-4%)")
    for _ in range(stats.big_chances_missed):
        add("BCM", -2.0, "😬 Big chance missed (-2%)")

    # ── Passing & Midfield ────────────────────────────────────────────────────
    if stats.pass_accuracy >= 90:
        add("PASS90", +3.0, f"🎯 Pass accuracy {stats.pass_accuracy:.0f}% (+3%)")
    # Progressive passes: only +1% per every 2 progressive passes
    prog_bonus = stats.progressive_passes // 2
    for _ in range(prog_bonus):
        add("PROG_PASS", +1.0, "↗ Progressive passes (+1%)")
    for _ in range(stats.interceptions):
        add("INTERCEPT", +1.5, "✂️ Interception (+1.5%)")
    for _ in range(stats.times_dispossessed):
        add("DISPOSS", -2.0, "😓 Dispossessed (-2%)")

    # ── Defensive ─────────────────────────────────────────────────────────────
    if stats.clean_sheet and stats.minutes_played >= 60:
        add("CLEAN_SHEET", +5.0, "🧱 Clean sheet (+5%)")
    for _ in range(stats.saves):
        add("SAVE", +1.5, "🧤 Save (+1.5%)")
    for _ in range(stats.tackles_won):
        add("TACKLE", +1.0, "💪 Tackle won (+1%)")
    for _ in range(stats.goals_conceded):
        add("GOAL_CONC", -2.0, "😔 Goal conceded (-2%)")
    for _ in range(stats.own_goals):
        add("OWN_GOAL", -6.0, "💀 Own goal (-6%)")
    for _ in range(stats.errors_to_goal):
        add("ERROR_GOAL", -5.0, "🚨 Error leading to goal (-5%)")

    # ── Discipline ────────────────────────────────────────────────────────────
    for _ in range(stats.yellow_cards):
        add("YELLOW", -1.0, "🟨 Yellow card (-1%)")
    for _ in range(stats.red_cards):
        add("RED", -5.0, "🟥 Red card (-5%)")

    # ── Team result ───────────────────────────────────────────────────────────
    if stats.team_won:
        add("TEAM_WIN", +1.0, "🏆 Team won (+1%)")
    if stats.team_advanced:
        add("TEAM_ADV", +3.0, "🚀 Team advanced (+3%)")
    if stats.team_eliminated:
        add("TEAM_ELIM", -4.0, "💔 Team eliminated (-4%)")

    # ── Match rating ──────────────────────────────────────────────────────────
    if stats.match_rating is not None and stats.minutes_played >= 45:
        delta, label = rating_to_delta(stats.match_rating)
        add("RATING", delta, f"⭐ {label}")

    return changes


def apply_player_stats(stats: PlayerMatchStats,
                       match_id: int | None = None) -> PlayerPriceResult | None:
    player = db.get_player(stats.player_id)
    if not player or stats.minutes_played == 0:
        return None

    changes   = calculate_deltas(stats)
    old_price = player["live_price"]
    new_price = old_price

    for ch in changes:
        new_price = new_price * (1 + ch.delta_pct / 100)
    new_price = max(0.50, round(new_price, 4))

    total_delta = ((new_price - old_price) / old_price) * 100
    summary     = " | ".join(f"{c.event_type}({c.delta_pct:+.1f}%)" for c in changes) or "No events"

    db.update_player_price(stats.player_id, new_price,
                           reason=summary, rating=stats.match_rating)
    for ch in changes:
        db.log_match_event(match_id, stats.player_id,
                           ch.event_type, ch.delta_pct, ch.description)

    return PlayerPriceResult(
        player_id       = stats.player_id,
        player_name     = player["name"],
        pos             = player["pos"],
        flag            = player.get("flag", ""),
        team            = player["team"],
        old_price       = old_price,
        new_price       = new_price,
        total_delta_pct = total_delta,
        changes         = changes,
        match_rating    = stats.match_rating,
    )


def process_full_match(match_id: int,
                       all_stats: list[PlayerMatchStats]) -> list[PlayerPriceResult]:
    results = []
    for stats in all_stats:
        r = apply_player_stats(stats, match_id)
        if r:
            results.append(r)
    db.mark_match_processed(match_id)
    return results


def get_market_summary() -> dict:
    players = db.get_all_players()
    for p in players:
        p["chg_pct"] = ((p["live_price"] - p["prev_price"]) / p["prev_price"] * 100) \
                        if p["prev_price"] > 0 else 0.0
    return {
        "top_gainers":   sorted(players, key=lambda x: x["chg_pct"], reverse=True)[:5],
        "top_losers":    sorted(players, key=lambda x: x["chg_pct"])[:5],
        "most_traded":   sorted(players, key=lambda x: x["volume"], reverse=True)[:5],
        "market_cap":    sum(p["live_price"] * 1_000_000 for p in players),
        "advancing":     sum(1 for p in players if p["chg_pct"] > 0),
        "declining":     sum(1 for p in players if p["chg_pct"] < 0),
        "total":         len(players),
    }
