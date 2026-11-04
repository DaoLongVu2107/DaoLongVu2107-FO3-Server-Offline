"""Test helpers: load the server module without starting it, in a throw-away data dir.

The server is imported once per process (as module "http_config", so career.startup and the
listening sockets never run). Sandbox points the save, config, backups, clock and capture
files at a temp dir and restores everything afterwards; the real gamedata/ is only read
(fifadb.sqlite, rosters). Tests that need the player database skip when
gamedata/fifadb.sqlite has not been extracted from fifadb.rar.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

SERVER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(SERVER, "gamedata", "fifadb.sqlite")


def load():
    if "http_config" in sys.modules:
        return sys.modules["http_config"]
    if SERVER not in sys.path:
        sys.path.insert(0, SERVER)
    argv, sys.argv = sys.argv, ["http_config.py", "0"]
    try:
        import http_config
    finally:
        sys.argv = argv
    return http_config


def J(reply):
    """Body of an endpoint reply (ctype, bytes) as JSON."""
    return json.loads(reply[1])


needs_db = unittest.skipUnless(os.path.isfile(DB), "can giai nen Server/gamedata/fifadb.rar truoc")


class Sandbox(unittest.TestCase):
    """Base class: self.hc is the server module, self.dir a fresh data dir per test."""

    def setUp(self):
        self.hc = load()  # first: puts Server/ on sys.path
        import career
        from career import clock, config
        self.career = career
        self.dir = tempfile.mkdtemp(prefix="fo3test_")
        self._saved = (self.hc.STATE, self.hc.LOG, clock._now, os.environ.get("FO3_DEV"))
        self.hc.STATE = os.path.join(self.dir, "state.json")
        self.hc.LOG = os.path.join(self.dir, "captures", "http_config.log")
        os.environ.pop("FO3_DEV", None)
        self.t = 1_800_000_000.0  # fake clock (2027-01-15); tests move it with self.at()
        clock._now = lambda: self.t
        clock._warned = False
        config.reload()

    def tearDown(self):
        from career import clock, config
        self.hc.STATE, self.hc.LOG, clock._now, dev = self._saved
        if dev is None:
            os.environ.pop("FO3_DEV", None)
        else:
            os.environ["FO3_DEV"] = dev
        shutil.rmtree(self.dir, ignore_errors=True)
        config._cache = None  # do not create the real gamedata/config.json

    def at(self, t):
        self.t = float(t)

    def write_json(self, name, obj):
        p = os.path.join(self.dir, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        return p

    def read_json(self, name):
        with open(os.path.join(self.dir, name), encoding="utf-8") as f:
            return json.load(f)

    def new_career(self, teamid=241, name="Test"):
        """A manager in slot 0 with that club's full squad, set as the default manager."""
        hc = self.hc
        assert J(hc.ep_create_coach(0, "", json.dumps({"id": teamid, "coachName": name}).encode()))["result"]
        spids = [p["spid"] for p in hc.roster(teamid)["team"]["players"]]
        assert J(hc.ep_new_team(0, "", json.dumps({"id": teamid, "spids": spids}).encode()))["result"]
        st = hc._state()
        st["defaultcoachid"] = hc.coach_id(0)
        hc._save(st)
        return hc._state()
