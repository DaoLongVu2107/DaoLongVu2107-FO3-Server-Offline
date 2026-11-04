"""gamedata/config.json: every balance number, with defaults in code.

A missing file is created from DEFAULTS so it can be edited; a broken one is reported and
ignored (defaults are used, the file is left alone so the edit is not lost). Keys missing from
the file fall back to DEFAULTS, so later milestones can add keys without touching old files.
Changes apply after restarting the server.
"""
import copy
import json
import os

DEFAULTS = {
    "backup": {"keep": 10},
    "clock": {"timezone_hours": 7, "rollback_tolerance_minutes": 10},
    # M1 - kinh te cot loi
    "economy": {
        "start_ep": 50000,
        "shop_free": False,
        "pack_markup": 1.3,           # pack price = expected card value x this
        "bundle_factor": 0.9,         # a bundle costs its contents x this
        "match_ep": {"win": 8000, "draw": 4000, "loss": 2000, "per_goal": 500, "max_goals": 5, "clean_sheet": 1000},
        "manager_mode_share": 0.5,    # Manager mode (the AI plays for you)
        "season_ep_per_rank": 2000,   # league season EP = (11 - rank) x this x difficulty
        "season_min_played_share": 0.5,
        "season_floor_share": 0.2,
        "scout_cooldown_hours": {"default_A01": 0, "default_B01": 6, "igr": 6, "vip": 12},
        "staff_prices": {"1": 10000, "2": 50000, "3": 150000},
        "item_prices": {"910001": 5000, "910004": 10000, "910002": 22000, "910005": 42000, "910006": 80000,
                        "910003": 120000, "911001": 8000, "911002": 35000, "911003": 190000, "3002": 20000},
        "blocked_products": [],       # extra itemids never sold (EP items / boxes / monthly are always blocked)
        "daily_rewards": [{"ep": 3000}, {"ep": 5000}, {"pack": 28007}, {"ep": 8000}, {"pack": 28006},
                          {"ep": 12000}, {"ep": 20000, "pack": 8223601}],
    },
    "difficulty": {
        "league": {"10": 0.5, "11": 0.65, "12": 0.8, "13": 0.95, "14": 1.1, "15": 1.25, "16": 1.4, "17": 1.6,
                   "18": 1.8, "19": 2.0, "20": 2.3, "21": 2.6, "22": 2.9, "23": 3.2, "24": 3.5},
        "cup": {"0": 0.5, "1": 0.8, "2": 1.2, "3": 1.8, "4": 2.5},
    },
    "unlocks": {
        "league_max_by_level": {"1": 12, "5": 14, "10": 16, "20": 19, "35": 21, "50": 23, "70": 24},
        "cup_max_by_level": {"1": 1, "10": 2, "35": 3, "70": 4},
        "igr_level": 20,
        "vip_level": 50,
    },
    "match": {"half_length": 60, "subs": 5, "bench": 7},
}

hc = None
_cache = None
_error = None


def install(module):
    global hc
    hc = module


def path():
    return os.path.join(os.path.dirname(hc.STATE), "config.json")


def merge(base, over):
    """DEFAULTS deep-merged with the file's values (dicts merge, everything else replaces)."""
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def reload(create=True):
    """Read config.json again (creating it from DEFAULTS if missing, unless create=False) and
    return the merged config."""
    global _cache, _error
    p = path()
    _error = None
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("config.json phai la mot object JSON")
    except FileNotFoundError:
        data = {}
        if not create:
            _cache = merge(DEFAULTS, data)
            return _cache
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(DEFAULTS, f, indent=2, ensure_ascii=False)
        except OSError as e:
            _error = f"khong tao duoc {p}: {e}"
    except (OSError, ValueError) as e:
        data = {}
        _error = f"config.json loi, dung gia tri mac dinh: {e}"
        print(f"[career] CANH BAO: {_error}", flush=True)
    _cache = merge(DEFAULTS, data)
    return _cache


def get(*keys):
    """config value at keys, e.g. get("backup", "keep")."""
    v = _cache if _cache is not None else reload(create=False)
    for k in keys:
        v = v[k]
    return v


def error():
    """The last load problem (None when config.json was fine)."""
    return _error
