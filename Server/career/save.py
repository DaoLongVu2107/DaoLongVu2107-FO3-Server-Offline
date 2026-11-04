"""Save versioning, upgrades, atomic writes and backups for gamedata/state.json.

- state["version"]: CURRENT_VERSION. A save without it is version 0 (made before career mode).
- MIGRATIONS[n] upgrades a save from version n to n + 1; startup() runs the missing ones,
  after a backup tagged "truoc-nang-cap".
- hc._save is wrapped: it stamps the version and writes through a temp file + os.replace, so a
  crash mid-write can no longer leave a half-written save.
- Backups: gamedata/backups/state_<YYYY-mm-dd_HHMMSS>[_<tag>].json, newest `keep` kept; a
  launch backup is skipped when the save is identical to the newest backup.

Also a small command line tool (run it with the server stopped):
    python Server/career/save.py list
    python Server/career/save.py restore      (asks which backup)
"""
import json
import os
import shutil
import sys
import time

CURRENT_VERSION = 2
PREFIX, SUFFIX = "state_", ".json"

hc = None


def _m0_to_1(st):
    """v0 -> v1: version stamp + a meta block; nothing else changes."""
    st.setdefault("meta", {})["upgraded_from_v0"] = int(time.time())


def _m1_to_2(st):
    """v1 -> v2 (M1 economy): managers whose EP was never stored relied on the old 1,000,000
    default; store it so the new 50,000 start EP only applies to new managers."""
    for c in st.get("coaches", []):
        c.setdefault("ep", 1_000_000)


MIGRATIONS = {0: _m0_to_1, 1: _m1_to_2}


def install(module):
    global hc
    hc = module
    orig = module._save

    def _save(st):
        st["version"] = CURRENT_VERSION
        write_atomic(module.STATE, st)

    _save.__wrapped__ = orig
    module._save = _save


def version_of(st):
    v = st.get("version", 0)
    return v if isinstance(v, int) and v >= 0 else 0


def migrate(st):
    """Upgrade st in place to CURRENT_VERSION; returns the list of versions it went through."""
    done = []
    v = version_of(st)
    if v > CURRENT_VERSION:
        raise ValueError(f"save phien ban {v} moi hon server ({CURRENT_VERSION}): hay cap nhat server")
    while v < CURRENT_VERSION:
        MIGRATIONS[v](st)
        v += 1
        st["version"] = v
        done.append(v)
    return done


def write_atomic(path, st):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f)
        f.flush()
        os.fsync(f.fileno())
    for attempt in range(5):  # Windows: an antivirus scan can hold the save open for a moment
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.1 * (attempt + 1))


def backup_dir(state_path):
    return os.path.join(os.path.dirname(state_path), "backups")


def list_backups(state_path):
    """Backup file paths, newest first."""
    d = backup_dir(state_path)
    try:
        names = [n for n in os.listdir(d) if n.startswith(PREFIX) and n.endswith(SUFFIX)]
    except FileNotFoundError:
        return []
    return [os.path.join(d, n) for n in sorted(names, reverse=True)]


def _same(a, b):
    try:
        with open(a, "rb") as fa, open(b, "rb") as fb:
            return fa.read() == fb.read()
    except OSError:
        return False


def backup(state_path, keep, tag="", now=None, skip_if_same=False):
    """Copy the save into backups/; returns the new path, or None (no save / unchanged)."""
    if not os.path.isfile(state_path):
        return None
    existing = list_backups(state_path)
    if skip_if_same and existing and _same(state_path, existing[0]):
        return None
    d = backup_dir(state_path)
    os.makedirs(d, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d_%H%M%S", time.localtime(time.time() if now is None else now))
    name = f"{PREFIX}{stamp}{'_' + tag if tag else ''}{SUFFIX}"
    dest = os.path.join(d, name)
    n = 1
    while os.path.exists(dest):  # two backups in the same second
        dest = os.path.join(d, f"{PREFIX}{stamp}-{n}{'_' + tag if tag else ''}{SUFFIX}")
        n += 1
    shutil.copy2(state_path, dest)
    for old in list_backups(state_path)[max(1, int(keep)):]:
        try:
            os.remove(old)
        except OSError:
            pass
    return dest


def startup(cfg):
    """Launch backup, then upgrade the save if it is older than CURRENT_VERSION."""
    path, keep = hc.STATE, cfg["backup"]["keep"]
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        st = json.load(f)
    if version_of(st) >= CURRENT_VERSION:
        return backup(path, keep, skip_if_same=True)
    made = backup(path, keep, tag="truoc-nang-cap")  # the only backup this launch needs
    steps = migrate(st)
    write_atomic(path, st)
    print(f"[career] nang cap save: v{steps[0] - 1} -> v{steps[-1]}", flush=True)
    return made


def restore(state_path, src, keep=10):
    """Put backup src back as the save (the current save is backed up first, tag truoc-khoi-phuc)."""
    with open(src) as f:
        json.load(f)  # refuse a broken backup
    backup(state_path, keep, tag="truoc-khoi-phuc")
    shutil.copy2(src, state_path)


def _cli(argv):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state = os.path.join(here, "gamedata", "state.json")
    items = list_backups(state)
    cmd = argv[1] if len(argv) > 1 else "list"
    if not items:
        print("Chua co ban sao luu nao trong", backup_dir(state))
        return 1
    for i, p in enumerate(items, 1):
        print(f"{i:3d}. {os.path.basename(p)}  ({os.path.getsize(p) // 1024} KB)")
    if cmd != "restore":
        return 0
    print("\nHay TAT server (cua so 'FO3 Offline Server') truoc khi khoi phuc.")
    pick = input("Chon so ban sao luu de khoi phuc (Enter de huy): ").strip()
    if not pick.isdigit() or not 1 <= int(pick) <= len(items):
        print("Da huy.")
        return 1
    restore(state, items[int(pick) - 1])
    print("Da khoi phuc:", os.path.basename(items[int(pick) - 1]))
    print("Save hien tai truoc do da duoc sao luu voi ten ..._truoc-khoi-phuc.json")
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv))
