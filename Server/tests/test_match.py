import json
import os

from harness import J, Sandbox, needs_db


def end_body(me, opp, gh, ga, **extra):
    return json.dumps({"home": {"id": me, "score": gh, "players": []},
                       "away": {"id": opp, "score": ga, "players": []},
                       "myTeam": "home", "opponentTeam": "away", **extra}).encode()


class MatchLogTest(Sandbox):
    def lines(self):
        from career import matchlog
        with open(matchlog.path(), encoding="utf-8") as f:
            return [json.loads(ln) for ln in f]

    def test_route_uses_the_logging_wrapper(self):
        fn = next(fn for pat, fn in self.hc.ROUTES if pat.pattern.endswith("/end"))
        self.assertTrue(hasattr(fn, "__wrapped__"))

    def test_broken_body_is_logged_without_error(self):
        from career import matchlog
        matchlog.record("abc", b"khong phai json")
        self.assertEqual(self.lines()[0]["stats"], {"_raw": "khong phai json"})

    @needs_db
    def test_training_match_is_logged(self):
        self.new_career()
        res = J(self.hc.ep_match_campaign("", b""))
        mid = res["resources"][0]["body"]["id"]
        me = self.hc.my_teamid(self.hc._state())
        out = J(self.hc.route(f"/match/{mid}/end")("", end_body(me, 243, 1, 0)))
        self.assertTrue(out["result"])
        rec = self.lines()[-1]
        self.assertEqual(rec["match"], mid)
        self.assertIsNone(rec["type"])  # training matches are not kept in the save

    @needs_db
    def test_cup_match_end_is_logged_and_rewarded(self):
        st = self.new_career()
        ep0 = self.hc.coach_me(st, 0)["money"]["ep"]
        cup = J(self.hc.ep_cup_new("", json.dumps({"metaid": 1, "difficulty": 1}).encode()))
        cupid = cup["resources"][0]["body"]["_id"]
        res = J(self.hc.ep_cup_match(cupid, "", b""))
        self.assertTrue(res["result"], res)
        mid = res["resources"][0]["body"]["id"]
        me = self.hc.my_teamid(self.hc._state())
        opp = self.hc._state()["cup_pending"]["away"]
        if opp == me:
            opp = self.hc._state()["cup_pending"]["home"]
        out = J(self.hc.route(f"/match/{mid}/end")("", end_body(me, opp, 2, 1, possession={"home": 55, "away": 45})))
        self.assertTrue(out["result"])
        rec = self.lines()[-1]
        self.assertEqual((rec["match"], rec["type"], rec["difficulty"]), (mid, "Cup_PvE", 1))
        self.assertEqual(rec["stats"]["possession"]["home"], 55)
        st = self.hc._state()
        self.assertGreater(self.hc.coach_me(st, 0)["money"]["ep"], ep0)  # the original handler still ran
        self.assertEqual(st["match"]["stage"], "closed")


class SmokeTest(Sandbox):
    def test_server_time(self):
        self.assertIn("timestamp", J(self.hc.ep_server_time("", b"")))

    @needs_db
    def test_new_career_save_has_version(self):
        from career import save
        st = self.new_career()
        self.assertEqual(st["version"], save.CURRENT_VERSION)
        self.assertTrue(os.path.isfile(self.hc.STATE))
