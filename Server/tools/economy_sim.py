"""Mo phong kinh te (M1): how much EP / coach level a schedule earns with the current config.

    python -I Server/tools/economy_sim.py [--weekend-hours 1.5] [--match-minutes 17]

Uses the server's own numbers (config.json if present, else the defaults; coach exp curve,
card prices), with a simple expected-value player model:
- every match at the highest league / cup difficulty the coach level unlocks;
- result there: win 50%, draw 22%, loss 28%; 1.8 goals scored, 30% clean sheets;
- 70% league matches (18 per season, all played, finishing 3rd, sponsor goal met half the
  time), 30% cup matches (6 per cup, knocked out in the semi-final on average);
- daily login reward every day. Nothing is spent: "total EP" is all EP earned.
Card prices are today's (before M2 re-prices cards), so the "best card" column is a guide.
"""
import argparse
import os
import sys

SERVER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SERVER)
argv, sys.argv = sys.argv, ["http_config.py", "0"]
import http_config as hc  # noqa: E402  (loads the server without starting it)
sys.argv = argv
from career import config, economy  # noqa: E402

WIN, DRAW, LOSS = 0.50, 0.22, 0.28
GOALS, CLEAN = 1.8, 0.30
LEAGUE_SHARE, SEASON_MATCHES, RANK, SPONSOR_HIT = 0.7, 18, 3, 0.5
CUP_MATCHES, CUP_SHARE_OF_PRIZE = 6, 0.35
LEADERS_EP = 12000  # sum of the season's leader rewards before scaling


def level_of(exp):
    level = 1
    while level < hc.COACH_MAX_LEVEL and exp >= hc.coach_need(level):
        exp -= hc.coach_need(level)
        level += 1
    return level


def match_ep(mult):
    e = config.get("economy", "match_ep")
    base = WIN * e["win"] + DRAW * e["draw"] + LOSS * e["loss"]
    return base * mult + min(GOALS, e["max_goals"]) * e["per_goal"] + CLEAN * e["clean_sheet"]


def match_exp(mult):
    return (WIN * hc.EXP_WIN[0] + DRAW * hc.EXP_DRAW[0] + LOSS * hc.EXP_LOSS[0]) * mult


def season_ep(level_d):
    mult = economy.league_mult(level_d)
    per_rank = config.get("economy", "season_ep_per_rank")
    import json
    with open(os.path.join(hc.RESPONSES, "static_db_LEAGUE2REWARD.json")) as f:
        sponsor = json.load(f)["sponsor"]["1"].get(str(level_d), {}).get("count", 0)
    return (hc.LEAGUE_SIZE - RANK + 1) * per_rank * mult + LEADERS_EP * mult + SPONSOR_HIT * sponsor


def best_card(ep):
    """Highest client rating whose +1 card costs at most ep (today's price curve)."""
    best = None
    for ovr in range(50, 121):
        if hc.stat_price(ovr) * hc.GRADE_PRICE[1] <= ep:
            best = ovr
    return best


def run(weekend_hours, match_minutes, hours_total=300):
    week_hours = 5 * 0.5 + 2 * weekend_hours
    daily = config.get("economy", "daily_rewards")
    login_ep_per_day = sum(r.get("ep", 0) for r in daily) / len(daily)
    marks = [1, 5, 10, 20, 50, 100, 150, 200, 250, 300]
    exp = ep = 0.0
    played = 0
    rows, last = [], (0, 0.0)
    minutes, step = 0.0, match_minutes
    while minutes < hours_total * 60:
        st_level = level_of(exp)
        lv_league = int(economy._by_level(config.get("unlocks", "league_max_by_level"), st_level))
        lv_cup = int(economy._by_level(config.get("unlocks", "cup_max_by_level"), st_level))
        league = (played % 10) < LEAGUE_SHARE * 10
        mult = economy.league_mult(lv_league) if league else economy.cup_mult(lv_cup)
        ep += match_ep(mult)
        exp += match_exp(mult)
        played += 1
        if league and played % round(SEASON_MATCHES / LEAGUE_SHARE) == 0:
            ep += season_ep(lv_league)
            exp += (hc.LEAGUE_SIZE - RANK + 1) * 100
        if not league and played % round(CUP_MATCHES / (1 - LEAGUE_SHARE)) == 0:
            ep += hc.CUPS[0]["bestrewards"][-1][0]["count"] * CUP_SHARE_OF_PRIZE * economy.cup_mult(lv_cup)
        minutes += step
        days = minutes / 60 / week_hours * 7
        h = minutes / 60
        while marks and h >= marks[0]:
            mark = marks.pop(0)
            total = ep + login_ep_per_day * days
            rate = (total - last[1]) / max(1e-9, mark - last[0])
            rows.append((mark, days / 7, st_level, lv_league - 9, lv_cup, total, rate, best_card(total)))
            last = (mark, total)
    print(f"Lich: thu 2-6 x 30 phut + thu 7, CN x {weekend_hours} gio = {week_hours:.1f} gio/tuan; "
          f"{match_minutes} phut/tran\n")
    print(f"{'Gio':>5} {'Tuan':>6} {'Cap HLV':>8} {'League':>7} {'Cup':>4} {'Tong EP':>13} {'EP/gio':>9} {'The +1 mua duoc':>16}")
    for mark, weeks, lvl, lg, cup, total, rate, card in rows:
        lg_name = f"{lg}" if lg <= 10 else f"TT{lg - 10}"
        print(f"{mark:>5} {weeks:>6.1f} {lvl:>8} {lg_name:>7} {cup:>4} {total:>13,.0f} {rate:>9,.0f} {('OVR ' + str(card)) if card else '-':>16}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--weekend-hours", type=float, default=1.5)
    ap.add_argument("--match-minutes", type=float, default=17)
    a = ap.parse_args()
    run(a.weekend_hours, a.match_minutes)
