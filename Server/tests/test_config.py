import os

from harness import Sandbox


class ConfigTest(Sandbox):
    def test_missing_file_is_created_with_defaults(self):
        from career import config
        os.remove(config.path())  # setUp's reload() already made one
        cfg = config.reload()
        self.assertTrue(os.path.isfile(config.path()))
        self.assertEqual(cfg["backup"]["keep"], 10)
        self.assertEqual(config.get("clock", "timezone_hours"), 7)
        self.assertIsNone(config.error())

    def test_file_overrides_merge_with_defaults(self):
        from career import config
        self.write_json("config.json", {"backup": {"keep": 3}, "extra": 1})
        cfg = config.reload()
        self.assertEqual(cfg["backup"]["keep"], 3)
        self.assertEqual(cfg["clock"]["rollback_tolerance_minutes"], 10)  # untouched default
        self.assertEqual(cfg["extra"], 1)

    def test_broken_file_uses_defaults_and_is_kept(self):
        from career import config
        with open(config.path(), "w") as f:
            f.write("{ day la loi")
        cfg = config.reload()
        self.assertEqual(cfg["backup"]["keep"], 10)
        self.assertIsNotNone(config.error())
        with open(config.path()) as f:
            self.assertEqual(f.read(), "{ day la loi")  # the player's edit is not overwritten
