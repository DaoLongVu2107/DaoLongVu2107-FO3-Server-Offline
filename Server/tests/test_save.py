import json
import os

from harness import Sandbox


class SaveTest(Sandbox):
    def test_migrate_v0(self):
        from career import save
        st = {"coaches": [], "defaultcoachid": "", "teams": {}}
        self.assertEqual(save.migrate(st), [1])
        self.assertEqual(st["version"], save.CURRENT_VERSION)
        self.assertIn("upgraded_from_v0", st["meta"])
        self.assertEqual(save.migrate(st), [])  # already current

    def test_newer_save_is_refused(self):
        from career import save
        with self.assertRaises(ValueError):
            save.migrate({"version": save.CURRENT_VERSION + 1})

    def test_save_is_atomic_and_versioned(self):
        from career import save
        self.hc._save({"coaches": [], "teams": {}})
        st = self.read_json("state.json")
        self.assertEqual(st["version"], save.CURRENT_VERSION)
        self.assertFalse(os.path.exists(self.hc.STATE + ".tmp"))

    def test_backup_rotation_keeps_newest(self):
        from career import save
        made = []
        for i in range(5):
            self.write_json("state.json", {"n": i})
            made.append(save.backup(self.hc.STATE, keep=3, now=1_800_000_000 + i))
        left = save.list_backups(self.hc.STATE)
        self.assertEqual(len(left), 3)
        self.assertEqual(left, list(reversed(made[2:])))

    def test_launch_backup_skips_unchanged_save(self):
        from career import save
        self.write_json("state.json", {"n": 1})
        self.assertIsNotNone(save.backup(self.hc.STATE, 10, skip_if_same=True, now=1))
        self.assertIsNone(save.backup(self.hc.STATE, 10, skip_if_same=True, now=2))
        self.write_json("state.json", {"n": 2})
        self.assertIsNotNone(save.backup(self.hc.STATE, 10, skip_if_same=True, now=3))

    def test_no_save_no_backup(self):
        from career import config, save
        self.assertIsNone(save.startup(config.get()))
        self.assertEqual(save.list_backups(self.hc.STATE), [])

    def test_startup_upgrades_old_save_after_backup(self):
        from career import config, save
        self.write_json("state.json", {"coaches": [], "defaultcoachid": "", "teams": {}})
        save.startup(config.get())
        self.assertEqual(self.read_json("state.json")["version"], save.CURRENT_VERSION)
        names = [os.path.basename(p) for p in save.list_backups(self.hc.STATE)]
        self.assertEqual(len(names), 1, names)  # no extra identical launch backup
        self.assertTrue(names[0].endswith("_truoc-nang-cap.json"), names)
        old = next(p for p in save.list_backups(self.hc.STATE) if p.endswith("_truoc-nang-cap.json"))
        with open(old) as f:
            self.assertNotIn("version", json.load(f))  # the backup is the untouched v0 save

    def test_restore(self):
        from career import save
        self.write_json("state.json", {"n": "cu"})
        old = save.backup(self.hc.STATE, 10, now=1)
        self.write_json("state.json", {"n": "moi"})
        save.restore(self.hc.STATE, old)
        self.assertEqual(self.read_json("state.json"), {"n": "cu"})
        names = [os.path.basename(p) for p in save.list_backups(self.hc.STATE)]
        self.assertTrue(any(n.endswith("_truoc-khoi-phuc.json") for n in names), names)

    def test_restore_refuses_broken_backup(self):
        from career import save
        self.write_json("state.json", {"n": 1})
        bad = os.path.join(self.dir, "bad.json")
        with open(bad, "w") as f:
            f.write("{loi")
        with self.assertRaises(ValueError):
            save.restore(self.hc.STATE, bad)
        self.assertEqual(self.read_json("state.json"), {"n": 1})
