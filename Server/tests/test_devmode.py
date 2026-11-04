import os

from harness import Sandbox


class DevModeTest(Sandbox):
    def setUp(self):
        super().setUp()
        import admin
        admin.hc = self.hc
        self.admin = admin

    def test_cheats_locked_by_default(self):
        from career import devmode
        for name in ("ep", "player_add", "player_grade", "player_remove", "give_pack", "bag_send",
                     "daily_set", "daily_reset", "daily_grant", "scouts_reset"):
            with self.assertRaises(self.admin.AdminError, msg=name) as e:
                self.admin.API[name]({})
            self.assertEqual(str(e.exception), devmode.LOCKED_MSG)

    def test_read_only_and_squad_moves_stay_open(self):
        for name in self.admin.READ_ONLY | {"player_team"}:
            self.assertFalse(getattr(self.admin.API[name], "_career_locked", False), name)

    def test_mode_endpoint(self):
        m = self.admin.API["mode"]({})
        self.assertFalse(m["dev"])
        os.environ["FO3_DEV"] = "1"
        self.assertTrue(self.admin.API["mode"]({})["dev"])

    def test_dev_mode_unlocks(self):
        from career.devmode import _locked
        gated = _locked(lambda p: {"ok": p}, self.admin.AdminError)
        with self.assertRaises(self.admin.AdminError):
            gated(1)
        os.environ["FO3_DEV"] = "1"
        self.assertEqual(gated(1), {"ok": 1})
