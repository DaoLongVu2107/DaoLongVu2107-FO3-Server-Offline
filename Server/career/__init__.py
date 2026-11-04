"""Che do Su nghiep (career mode) for the FO3 offline server.

Everything new lives in this package so http_config.py (the original author's file) only needs
two hook lines: career.install(module) at import time and career.startup(module) in __main__.
Like staff_service.install, install() patches the server module in place: wrapped functions
are looked up through the module's globals at call time, so callers see the new behaviour.

Data files all sit next to the save (os.path.dirname(hc.STATE)), so a test that points
hc.STATE at a temp dir moves config.json, backups/ and clock.json with it.
"""
from . import clock, config, devmode, economy, matchlog, save

hc = None


def install(module):
    """Hook the career modules into http_config (called once when it is imported)."""
    global hc
    hc = module
    for m in (config, save, clock, devmode, matchlog, economy):
        m.install(module)


def startup(module):
    """One-off work before the server starts listening: config file, save backup and
    upgrade, clock check, banners."""
    cfg = config.reload()
    economy.apply()  # module values from the (re)loaded config.json
    print(f"[career] config: {config.path()}", flush=True)
    made = save.startup(cfg)
    if made:
        print(f"[career] sao luu save: {made}", flush=True)
    print(f"[career] phien ban save: {save.CURRENT_VERSION}", flush=True)
    if not clock.check():
        print("[career] CANH BAO: gio may dang som hon lan chay truoc -> tam dung qua tang", flush=True)
    if devmode.enabled():
        print("[career] ========== CHE DO DEV: cong cu cheat dang BAT ==========", flush=True)
