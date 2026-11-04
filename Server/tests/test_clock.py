from harness import Sandbox


class ClockTest(Sandbox):
    def test_forward_and_small_rollback_are_fine(self):
        from career import clock
        self.assertTrue(clock.check())
        self.at(self.t + 3600)
        self.assertTrue(clock.check())
        self.at(self.t - 5 * 60)  # inside the 10 minute tolerance
        self.assertTrue(clock.check())

    def test_rollback_blocks_until_clock_catches_up(self):
        from career import clock
        start = self.t
        self.assertTrue(clock.check())
        self.at(start - 3600)
        self.assertFalse(clock.check())
        self.assertTrue(clock.status()["rolled_back"])
        self.at(start + 1)
        self.assertTrue(clock.check())

    def test_daily_login_paused_while_rolled_back(self):
        from career import clock
        self.assertTrue(clock.check())
        self.at(self.t - 2 * 86400)
        # returns before touching the save, so no manager is needed here
        self.assertIsNone(self.hc.daily_login({"coaches": []}))

    def test_local_time_is_utc_plus_7(self):
        from career import clock
        self.assertEqual(clock.local_struct(0).tm_hour, 7)
