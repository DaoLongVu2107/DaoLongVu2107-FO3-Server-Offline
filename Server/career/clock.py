"""Device clock (the server runs on the player's PC, so time.time() is the PC clock).

check() remembers the latest time seen in gamedata/clock.json. When the clock goes back more
than clock.rollback_tolerance_minutes behind it, check() returns False until the clock passes
that point again: real-time rewards (daily login now; transfer sessions and missions later)
use it so turning the PC clock back does not hand them out twice. Moving the clock forward
cannot be detected offline.
"""
import json
import os
import time

from . import config

hc = None
_now = time.time  # tests replace this
_warned = False


def install(module):
    global hc
    hc = module
    orig = module.daily_login

    def daily_login(st, now=None):
        if now is None and not check():
            return None  # clock went back: no reward until it catches up
        return orig(st, now)

    daily_login.__wrapped__ = orig
    module.daily_login = daily_login


def path():
    return os.path.join(os.path.dirname(hc.STATE), "clock.json")


def now():
    return _now()


def _load():
    try:
        with open(path()) as f:
            return float(json.load(f).get("last_seen", 0))
    except (OSError, ValueError, AttributeError):
        return 0.0


def check():
    """True if the clock is not behind the latest time seen (and records the new latest)."""
    global _warned
    t, last = now(), _load()
    if t < last - 60 * config.get("clock", "rollback_tolerance_minutes"):
        if not _warned:
            _warned = True
            print(f"[career] CANH BAO: gio may lui {int((last - t) // 60)} phut so voi lan truoc; "
                  "qua tang theo gio that tam dung", flush=True)
        return False
    _warned = False
    if t > last:
        try:
            os.makedirs(os.path.dirname(path()), exist_ok=True)
            with open(path(), "w") as f:
                json.dump({"last_seen": t}, f)
        except OSError:
            pass
    return True


def status():
    t, last = now(), _load()
    return {"now": int(t), "last_seen": int(last),
            "rolled_back": t < last - 60 * config.get("clock", "rollback_tolerance_minutes")}


def local_struct(ts=None):
    """time.struct_time in the game's timezone (config clock.timezone_hours, default UTC+7)."""
    return time.gmtime((now() if ts is None else ts) + 3600 * config.get("clock", "timezone_hours"))
