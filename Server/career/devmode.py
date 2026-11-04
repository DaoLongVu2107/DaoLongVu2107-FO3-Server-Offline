"""Che do DEV: the admin page's cheat tools only work with FO3_DEV=1.

Career mode has no sandbox. The admin API calls that change the save (EP, add/remove/grade
players, packs, Bag gifts, daily reward table, scout reset...) answer an error unless the
server runs with FO3_DEV=1 (3_Choi_Che_Do_DEV.bat). Read-only calls keep working. The check
runs on every call, so it follows the environment the server was started with.
Adds GET /api/mode {dev, save_version, clock} for the page's banner.
"""
import os

from . import clock, save

# changes that are ordinary squad management, not cheats (the game itself can do them)
ALLOWED = {"player_team"}
LOCKED_MSG = ("Da khoa trong che do Su nghiep. Chi dung duoc khi chay "
              "3_Choi_Che_Do_DEV.bat (FO3_DEV=1).")


def enabled():
    return os.environ.get("FO3_DEV", "") == "1"


def install(module):
    import admin  # admin.API is filled when admin.py is imported
    for name, fn in list(admin.API.items()):
        if name in admin.READ_ONLY or name in ALLOWED or getattr(fn, "_career_locked", False):
            continue
        admin.API[name] = _locked(fn, admin.AdminError)
    admin.API["mode"] = lambda p: {"dev": enabled(), "save_version": save.CURRENT_VERSION, "clock": clock.status()}
    admin.READ_ONLY.add("mode")


def _locked(fn, error):
    def call(p):
        if not enabled():
            raise error(LOCKED_MSG)
        return fn(p)
    call._career_locked = True
    call.__wrapped__ = fn
    return call
