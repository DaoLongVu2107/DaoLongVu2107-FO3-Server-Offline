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


def reload():
    """Read config.json again (creating it from DEFAULTS if missing) and return the merged config."""
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
    v = _cache if _cache is not None else reload()
    for k in keys:
        v = v[k]
    return v


def error():
    """The last load problem (None when config.json was fine)."""
    return _error
