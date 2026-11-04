"""M1 - Kinh te cot loi: EP is earned by playing, nothing prints EP, harder AI pays more.

Hooks (all numbers in config.json "economy" / "difficulty" / "unlocks" / "match"):
- Shop: real prices (packs = expected card value x pack_markup; items and bundles priced),
  EP-printing products out of every shop list and refused by /shop/purchase. Items already in
  the inventory or the Bag keep working.
- Match reward: base by result x difficulty multiplier + goal / clean sheet bonus; coach and
  player exp x the same multiplier; Manager mode (AI plays) gets manager_mode_share.
- League season and cup rewards x difficulty; the season reward also scales with the share of
  league matches actually played (simulated seasons pay little).
- Coach level unlocks league / cup difficulty, the PC-cafe (igr) and VIP perks (transfer fee
  discount, the igr / VIP scouts and trade extras).
- Scout cooldowns, match length / substitutes, daily login table, start EP, staff prices.
"""
import json

from . import config, devmode

hc = None

LEAGUE_TYPES = ("League_2_league", "League_2_league_MGR")
MANAGER_TYPE = "League_2_league_MGR"


def install(module):
    global hc
    hc = module
    _wrap("shop_price", lambda orig: shop_price)
    _wrap("use_item_def", _priced_item_def)
    _wrap("package_def", _priced_package_def)
    _wrap("shop_list", _sellable_shop_list)
    hc.MP_SHOP = tuple(i for i in hc.MP_SHOP if i not in blocked())
    hc.SPECIAL = tuple(i for i in hc.SPECIAL if i not in blocked())
    global _SCOUTS0
    _SCOUTS0 = hc.SCOUTS
    _wrap("ep_shop_purchase", _guard_purchase)
    _wrap("daily_table", lambda orig: lambda: orig() if devmode.enabled() else config.get("economy", "daily_rewards"))
    _wrap("match_reward", lambda orig: match_reward)
    _wrap("cup_reward_ep", lambda orig: lambda cup: int(orig(cup) * cup_mult(cup.get("difficulty", 0))))
    _wrap("ep_l2_end", _scaled_season_end)
    hc.ENDPOINTS["/league2/reward"] = ep_l2_reward
    _wrap("l2_me", _gated_l2_me)
    _wrap("ep_l2_calendar", _gated_calendar)
    _wrap("ep_cup_new", _gated_cup_new)
    _wrap("coach_me", _perks_coach_me)
    _wrap("sale_net", lambda orig: lambda o: sale_net(o))
    _wrap("offer_list", lambda orig: lambda st: dict(orig(st), boost=boost_for(st)))
    hc.ENDPOINTS["/transfer/my/boostfactor"] = lambda q, b: hc._json(boost_for(hc._state()))
    _wrap("coach_scouters", lambda orig: lambda st, slot: [s for s in orig(st, slot) if scout_open(st, s["key"])])
    _wrap("ep_trade3_proposal", _guard_trade3)
    _wrap("trade_props", lambda orig: lambda give, rng: _drop_locked_extras(orig(give, rng)))
    _wrap("trade3_props", lambda orig: lambda give, scout, rng: _drop_locked_extras(orig(give, scout, rng)))
    _wrap("new_match", _match_settings)
    _wrap("ep_create_coach", _start_ep)
    apply()


_SCOUTS0 = ()


def apply():
    """Plain module values taken from config (again after startup reloads config.json)."""
    hc.SHOP_FREE = bool(config.get("economy", "shop_free"))
    cool = config.get("economy", "scout_cooldown_hours")
    hc.SCOUTS = tuple((k, sid, int(3600 * cool.get(k, c / 3600)), rng, q) for k, sid, c, rng, q in _SCOUTS0)
    hc.HALF_LENGTH = int(config.get("match", "half_length"))
    hc.START_EP = int(config.get("economy", "start_ep"))
    import staff_service
    for pack in staff_service.PACKS:
        price = config.get("economy", "staff_prices").get(str(pack["recruitid"]))
        if price is not None:
            pack["ep"] = int(price)
            pack["staffpack_desc"] = pack["staffpack_desc"].split(". ")[0] + f". {int(price):,} EP."


def _wrap(name, make):
    """module.name = make(original); the wrapper keeps the original as __wrapped__."""
    orig = getattr(hc, name)
    new = make(orig)
    new.__wrapped__ = orig
    setattr(hc, name, new)


# --------------------------------------------------------------------------- levels / multipliers
def coach_level(st):
    try:
        return hc.coach_levelinfo(hc.my_coach(st))["level"]
    except (StopIteration, KeyError):
        return 1


def _by_level(table, level):
    """Value of the highest "level" key <= level in a {"1": v, "5": v...} table."""
    keys = sorted(int(k) for k in table)
    return table[str(max([k for k in keys if k <= level] or keys[:1]))]


def league_max(st):
    return int(_by_level(config.get("unlocks", "league_max_by_level"), coach_level(st)))


def cup_max(st):
    return int(_by_level(config.get("unlocks", "cup_max_by_level"), coach_level(st)))


def league_mult(difficulty):
    t = config.get("difficulty", "league")
    return float(t.get(str(int(difficulty)), t[min(t, key=lambda k: abs(int(k) - int(difficulty)))]))


def cup_mult(difficulty):
    t = config.get("difficulty", "cup")
    return float(t.get(str(int(difficulty)), t[min(t, key=lambda k: abs(int(k) - int(difficulty)))]))


def match_mult(match):
    gs = match.get("gamesettings") or {}
    d = gs.get("difficulty", 0)
    return league_mult(d) if match.get("type") in LEAGUE_TYPES else cup_mult(d)


# --------------------------------------------------------------------------- shop
def blocked():
    """Products that print EP (or swap clubs): never sold in career mode."""
    out = set(int(i) for i in config.get("economy", "blocked_products"))
    for i, (_, _, typ, eff, _) in hc.ITEMS.items():
        if typ == "EP_LOTTERY" or typ == "TEAM_CHANGE":
            out.add(i)
        elif typ == "ITEM_LOTTERY" and any(isinstance(p, tuple) and p[0] == "ep" for _, p in eff.get("prizes", [])):
            out.add(i)
    for i, (_, _, contents, _) in hc.PACKAGES.items():
        if any(c == hc.EP_ITEM or c in out for c, _ in contents):
            out.add(i)
    out.update(hc.MONTHLY)  # every monthly pack pays EP daily
    for first, steps in hc.CHAINED.items():
        if any(s in out for s in steps):
            out.update(steps)
    return out


def sellable_entry(e, no=None):
    itemid = (e.get("product") or {}).get("itemid")
    return itemid not in (blocked() if no is None else no) and e.get("shopcategory") not in ("CHAINED", "MONTHLYPACK")


def _sellable_shop_list(orig):
    def shop_list(st):
        no = blocked()
        return [e for e in orig(st) if sellable_entry(e, no)]
    return shop_list


def shop_price(value, n):
    if hc.SHOP_FREE:
        return 0
    return hc.sig3(value * config.get("economy", "pack_markup") * n * (0.95 if n > 1 else 1))


def unit_price(itemid):
    """EP price of one itemid in the shop (packs, priced items); None if not for sale."""
    if itemid in hc.PACKS:
        return shop_price(hc.pack_price(itemid), 1)
    p = config.get("economy", "item_prices").get(str(itemid))
    return None if p is None else (0 if hc.SHOP_FREE else int(p))


def package_price(itemid):
    if hc.SHOP_FREE:
        return 0
    contents = hc.PACKAGES[itemid][2]
    parts = [unit_price(i) for i, _ in contents]
    if any(p is None for p in parts):
        return None
    return hc.sig3(sum(p * n for p, (_, n) in zip(parts, contents)) * config.get("economy", "bundle_factor"))


def _priced_item_def(orig):
    def use_item_def(itemid):
        d = orig(itemid)
        p = unit_price(itemid)
        if p is not None:
            d["bunches"] = [{"bunch": n, "price": hc.sig3(p * n * (0.95 if n > 1 else 1)) if p else 0}
                            for n in hc.PACK_BUNCHES]
        return d
    return use_item_def


def _priced_package_def(orig):
    def package_def(itemid):
        d = orig(itemid)
        if itemid in hc.PACKAGES:
            p = package_price(itemid)
            if p is not None:
                d["bunches"] = [{"bunch": 1, "price": p}]
        return d
    return package_def


def _guard_purchase(orig):
    def ep_shop_purchase(query, body):
        try:
            req = json.loads(body or b"{}")
            itemid = int(req.get("productid") or 0) or int(req.get("shopid") or 0) % hc.MP_SHOPID % hc.STSHOPID
        except (ValueError, TypeError, AttributeError):
            itemid = 0
        if itemid in blocked() or (itemid in hc.ITEMS and unit_price(itemid) is None) \
                or (itemid in hc.PACKAGES and package_price(itemid) is None):
            return hc._json({"result": False, "reason": "NOT_EXIST_PRODUCT"})
        return orig(query, body)
    return ep_shop_purchase


# --------------------------------------------------------------------------- match rewards
def match_reward(st, stats):
    """hc.match_reward with difficulty-scaled EP and exp (same reply shape)."""
    e = config.get("economy", "match_ep")
    match = st.get("match") or {}
    mult = match_mult(match)
    share = config.get("economy", "manager_mode_share") if match.get("type") == MANAGER_TYPE else 1.0
    me, opp = stats.get("myTeam", "home"), stats.get("opponentTeam", "away")
    g = lambda s: int((stats.get(s) or {}).get("score") or 0)
    gf, ga = g(me), g(opp)
    won, drew = gf > ga, gf == ga
    base = e["win"] if won else e["draw"] if drew else e["loss"]
    base_ep = round(base * mult * share)
    extra_ep = round((min(gf, e["max_goals"]) * e["per_goal"] + (e["clean_sheet"] if ga == 0 else 0)) * share)
    cexp, pexp = hc.EXP_WIN if won else hc.EXP_DRAW if drew else hc.EXP_LOSS
    cexp = round(cexp * mult * share)
    reward = lambda n, b=None, x=0: {"total": n, "detail": {"base": n if b is None else b, "extra": x}}
    prev, cur = hc.gain_exp(hc.my_coach(st), cexp, hc.coach_need, hc.COACH_MAX_LEVEL)
    team, done, players = st["teams"].get(str(hc._default_slot(st))) or {"players": []}, set(), []
    for s in (stats.get(me) or {}).get("players") or []:
        pid = int(s.get("spid") or 0) % 1000000
        mine = [p for p in team["players"] if int(p["spid"]) % 1000000 == pid and hc.iid(p) not in done]
        p = next((p for p in mine if hc.in_squad(team, p)), mine[0] if mine else None)
        if p is None:
            continue
        n = round((pexp + 20 * int(s.get("goals") or 0) + 10 * int(s.get("assists") or 0)) * mult * share)
        pprev, pcur = hc.gain_exp(p, n, hc.player_need, hc.PLAYER_MAX_LEVEL)
        done.add(hc.iid(p))
        players.append({"id": hc.iid(p), "spid": p["spid"], "prev": pprev, "current": pcur, "reward": reward(n)})
    if match.get("type") in LEAGUE_TYPES and st.get("league2"):
        lg = st["league2"]
        lg["played"] = lg.get("played", 0) + (0.5 if match.get("type") == MANAGER_TYPE else 1)
    return {"matchRewardBackType": 0, "extra": {"selected": {}, "availables": []}, "selected": [],
            "coach": {"reward": reward(cexp), "prev": prev, "current": cur},
            "money": {"reward": reward(base_ep + extra_ep, base_ep, extra_ep)},
            "players": players, "missions": [], "exptankinfo": {}, "multiplier": mult}


def season_share(lg):
    """Season reward factor from the share of my league matches played (not simulated)."""
    league = lg.get("league") or {}
    total = (league.get("maxround", 2 * (hc.LEAGUE_SIZE - 1) - 1) + 1) or 1
    played = lg.get("played", 0) / total
    full, floor = config.get("economy", "season_min_played_share"), config.get("economy", "season_floor_share")
    return 1.0 if played >= full else max(floor, played / full)


def _scaled_season_end(orig):
    def ep_l2_end(query, body):
        st = hc._state()
        lg = st.get("league2") or {}
        if not lg.get("league"):
            return orig(query, body)
        mult, share = league_mult(lg.get("difficultyselect", 10)), season_share(lg)
        before = hc.my_coach(st).get("ep", hc.START_EP)
        reply = orig(query, body)
        out = json.loads(reply[1])
        if not out.get("result"):
            return reply
        money = out["rewards"]["money"]["reward"]
        d = money["detail"]
        d["season"] = round(d["season"] * config.get("economy", "season_ep_per_rank") / 2000 * mult * share)
        d["leader"] = round(d["leader"] * mult * share)
        d["sponsor"] = round(d["sponsor"] * share)  # the sponsor table already rises with difficulty
        for k in ("ratings", "goals", "assists", "tackles", "passes", "saves"):
            for e in out.get("leaderRewards", {}).get(k, []):
                e["reward"]["count"] = round(e["reward"]["count"] * mult * share)
        money["total"] = d["season"] + d["leader"] + d["sponsor"]
        out["rewards"]["money"]["share"] = round(share, 2)
        st = hc._state()
        coach = hc.my_coach(st)
        coach["ep"] = before + money["total"]
        lg2 = st.get("league2") or {}
        if lg2.get("difficultyselect", 10) > league_max(st):  # no promotion past what is unlocked
            lg2["difficultyselect"] = league_max(st)
            out["promotion"]["next"] = lg2["difficultyselect"]
        hc._save(st)
        out["resources"] = hc.l2_resources(st)
        return hc._json(out)
    return ep_l2_end


def ep_l2_reward(query, body):
    """Creation screen's champion reward per level (0-9 normal, 10-14 ultimate)."""
    per_rank = config.get("economy", "season_ep_per_rank")
    return hc._json([{"ep": round(per_rank * hc.LEAGUE_SIZE * league_mult(10 + i)), "items": []} for i in range(15)])


# --------------------------------------------------------------------------- difficulty gates
def _gated_l2_me(orig):
    def l2_me(st):
        me = orig(st)
        top = league_max(st)
        me["difficultybest"] = top
        me["difficultyselect"] = min(int(me.get("difficultyselect") or 10), top)
        return me
    return l2_me


def _gated_calendar(orig):
    def ep_l2_calendar(query, body):
        try:
            req = json.loads(body or b"{}")
        except ValueError:
            req = {}
        top = league_max(hc._state())
        req["difficulty"] = min(max(int(req.get("difficulty") or 10), 10), top)
        return orig(query, json.dumps(req).encode())
    return ep_l2_calendar


def _gated_cup_new(orig):
    def ep_cup_new(query, body):
        try:
            d = int(json.loads(body or b"{}").get("difficulty") or 0)
        except (ValueError, TypeError, AttributeError):
            d = 0
        top = cup_max(hc._state())
        if d > top:
            return hc._json({"result": False, "reason": f"Can cap HLV cao hon de mo do kho nay (toi da hien tai: {top})"})
        return orig(query, body)
    return ep_cup_new


# --------------------------------------------------------------------------- perks (igr / vip)
def perks(st):
    lv = coach_level(st)
    return {"igr": lv >= config.get("unlocks", "igr_level"), "vip": lv >= config.get("unlocks", "vip_level")}


def boost_for(st):
    p = perks(st)
    return dict(hc.NO_BOOST, igr=hc.NO_BOOST["igr"] if p["igr"] else 0, vip=hc.NO_BOOST["vip"] if p["vip"] else 0)


def sale_net(o):
    b, fee = boost_for(hc._state()), o["completefee"]["base"]
    return o["price"] - fee + int(b["igr"] * fee) + int(b["vip"] * fee)


def _perks_coach_me(orig):
    def coach_me(st, slot):
        me = orig(st, slot)
        p = perks(st)
        me["igr"] = p["igr"]
        if not p["vip"]:
            me.update(vipDetail=0, vipExpireAt=0, vipStatus={})
        return me
    return coach_me


def scout_open(st, key):
    p = perks(st)
    return p["igr"] if key == "igr" else p["vip"] if key == "vip" else True


def _guard_trade3(orig):
    def ep_trade3_proposal(query, body):
        try:
            key = json.loads(body or b"{}").get("id")
        except (ValueError, AttributeError):
            key = None
        if key and not scout_open(hc._state(), key):
            return hc._json({"result": False, "reason": "invalid playerid"})
        return orig(query, body)
    return ep_trade3_proposal


def _drop_locked_extras(props):
    p = perks(hc._state())
    return [o for o in props if not o.get("boost") or p.get(o["boost"])]


# --------------------------------------------------------------------------- match settings, start
def _match_settings(orig):
    def new_match(mtype, left, right, **extra):
        m = orig(mtype, left, right, **extra)
        gs = m["gamesettings"]
        gs["halfLength"] = int(config.get("match", "half_length"))
        gs["availableSubs"] = int(config.get("match", "subs"))
        gs["subOnBench"] = int(config.get("match", "bench"))
        return m
    return new_match


def _start_ep(orig):
    def ep_create_coach(slot, query, body):
        reply = orig(slot, query, body)
        st = hc._state()
        c = next((c for c in st["coaches"] if c["slot"] == slot), None)
        if c is not None and "ep" not in c:
            c["ep"] = int(config.get("economy", "start_ep"))
            hc._save(st)
        return reply
    return ep_create_coach
