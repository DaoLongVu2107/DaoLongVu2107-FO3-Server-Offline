"""M1 - kinh te cot loi."""
import json

from harness import J, Sandbox, needs_db


def end_body(me, opp, gh, ga):
    return json.dumps({"home": {"id": me, "score": gh, "players": []}, "away": {"id": opp, "score": ga, "players": []},
                       "myTeam": "home", "opponentTeam": "away"}).encode()


class EconomyRulesTest(Sandbox):
    """No player database needed."""

    def test_ep_printing_products_are_blocked(self):
        from career import economy
        no = economy.blocked()
        for i in (501, 50028, 50029, 908, 50019, 50020, 50021, 50840, 50841, 119082304,  # EP items
                  50121, 50122, 50123, 50124, 50125, 200130000, 200130001,              # boxes with EP prizes
                  3001,                                                                  # club change
                  801, 50880, 80000001, 70000001, 70000002, 70000003,                    # packages / chain with EP
                  81000001, 81000002, 81000003):                                         # monthly packs
            self.assertIn(i, no, i)
        for i in (910001, 911003, 3002, 50881, 118012902, 912001, 912002):
            self.assertNotIn(i, no, i)

    def test_blocked_purchase_is_refused(self):
        for req in ({"productid": 50841}, {"shopid": self.hc.STSHOPID + 50841}, {"shopid": self.hc.MP_SHOPID + 501},
                    {"productid": 81000001}, {"productid": 3001}):
            self.assertEqual(J(self.hc.ep_shop_purchase("", json.dumps(req).encode()))["reason"], "NOT_EXIST_PRODUCT")

    def test_special_and_mp_shops_filtered(self):
        self.assertNotIn(50841, self.hc.SPECIAL)
        self.assertNotIn(501, self.hc.MP_SHOP)
        self.assertIn(3002, self.hc.MP_SHOP)

    def test_item_prices(self):
        d = self.hc.item_def(910002)
        self.assertEqual(d["bunches"][0]["price"], 22000)
        self.assertEqual(d["bunches"][1]["price"], self.hc.sig3(22000 * 10 * 0.95))
        exp_bundle = self.hc.item_def(912001)["bunches"][0]["price"]
        self.assertEqual(exp_bundle, self.hc.sig3((5 * 5000 + 3 * 22000 + 120000) * 0.9))

    def test_difficulty_tables(self):
        from career import economy
        self.assertEqual(economy.league_mult(10), 0.5)
        self.assertEqual(economy.league_mult(19), 2.0)
        self.assertEqual(economy.league_mult(24), 3.5)
        self.assertEqual(economy.cup_mult(4), 2.5)

    def test_unlock_tables(self):
        from career import economy
        table = {"1": 12, "5": 14, "10": 16}
        self.assertEqual(economy._by_level(table, 1), 12)
        self.assertEqual(economy._by_level(table, 7), 14)
        self.assertEqual(economy._by_level(table, 99), 16)

    def test_match_settings(self):
        side = {"team": {"teamid": 1}}
        gs = self.hc.new_match("Cup_PvE", side, {"team": {"teamid": 2}})["gamesettings"]
        self.assertEqual((gs["halfLength"], gs["availableSubs"], gs["subOnBench"]), (60, 5, 7))

    def test_scout_cooldowns(self):
        cool = {k: c for k, _, c, _, _ in self.hc.SCOUTS}
        self.assertEqual(cool, {"default_A01": 0, "default_B01": 6 * 3600, "igr": 6 * 3600, "vip": 12 * 3600})

    def test_daily_table_from_config(self):
        self.assertEqual(self.hc.daily_table()[0], {"ep": 3000})

    def test_v2_keeps_old_default_ep(self):
        from career import save
        st = {"version": 1, "coaches": [{"slot": 0}, {"slot": 1, "ep": 123}]}
        save.migrate(st)
        self.assertEqual([c["ep"] for c in st["coaches"]], [1_000_000, 123])


@needs_db
class EconomyGameTest(Sandbox):
    def setUp(self):
        super().setUp()
        self.st = self.new_career()

    def coach(self):
        return self.hc.my_coach(self.hc._state())

    def set_level(self, level):
        st = self.hc._state()
        self.hc.my_coach(st)["levelinfo"] = {"level": level, "exp": 0}
        self.hc._save(st)

    def test_new_coach_starts_with_50k(self):
        self.assertEqual(self.coach()["ep"], 50000)

    def test_pack_price_has_markup(self):
        price = self.hc.item_def(28006)["bunches"][0]["price"]
        self.assertEqual(price, self.hc.sig3(self.hc.pack_price(28006) * 1.3))
        self.assertGreater(price, 0)

    def test_shop_list_has_no_blocked_or_free_products(self):
        from career import economy
        no = economy.blocked()
        entries = self.hc.shop_list(self.hc._state())
        self.assertTrue(entries)
        for e in entries:
            itemid = e["product"]["itemid"]
            self.assertNotIn(itemid, no)
            self.assertNotIn(e["shopcategory"], ("CHAINED", "MONTHLYPACK"))
            self.assertGreater(e["product"]["staticdata"]["bunches"][0]["price"], 0, itemid)

    def test_buy_pack_costs_ep(self):
        price = self.hc.item_def(28006)["bunches"][0]["price"]
        out = J(self.hc.ep_shop_purchase("", json.dumps({"productid": 28006, "bunch": 0}).encode()))
        self.assertTrue(out["result"], out)
        self.assertEqual(self.coach()["ep"], 50000 - price)

    def test_existing_inventory_items_still_usable(self):
        st = self.hc._state()
        it = self.hc.inventory_add(self.hc.my_coach(st), 50021, 1)  # EP +1.000.000 owned from before
        self.hc._save(st)
        out = J(self.hc.ep_item_use(it["_id"], "", b"{}"))
        self.assertTrue(out["result"], out)
        self.assertEqual(self.coach()["ep"], 50000 + 1_000_000)

    def cup_match(self, difficulty, gf, ga):
        cup = J(self.hc.ep_cup_new("", json.dumps({"metaid": 1, "difficulty": difficulty}).encode()))
        self.assertTrue(cup.get("result"), cup)
        cupid = cup["resources"][0]["body"]["_id"]
        mid = J(self.hc.ep_cup_match(cupid, "", b""))["resources"][0]["body"]["id"]
        st = self.hc._state(); me = self.hc.my_teamid(st); p = st["cup_pending"]
        opp = p["away"] if p["home"] == me else p["home"]
        ep0 = self.coach()["ep"]
        self.hc.route(f"/match/{mid}/end")("", end_body(me, opp, gf, ga))
        return self.coach()["ep"] - ep0

    def test_match_reward_formula(self):
        # Cup "Ban chuyen" (1) = x0.8: win 8000*0.8 + 2 goals*500 + clean sheet 1000
        self.assertEqual(self.cup_match(1, 2, 0), round(8000 * 0.8) + 1000 + 1000)

    def test_loss_reward(self):
        self.assertEqual(self.cup_match(0, 1, 3), round(2000 * 0.5) + 500)

    def test_cup_difficulty_locked_by_level(self):
        out = J(self.hc.ep_cup_new("", json.dumps({"metaid": 1, "difficulty": 4}).encode()))
        self.assertFalse(out["result"])
        self.set_level(70)
        self.assertTrue(J(self.hc.ep_cup_new("", json.dumps({"metaid": 1, "difficulty": 4}).encode()))["result"])

    def test_league_difficulty_locked_by_level(self):
        st = self.hc._state()
        self.assertEqual(self.hc.l2_me(st)["difficultybest"], 12)
        self.hc.ep_l2_calendar("", json.dumps({"difficulty": 24, "sponsor": "1"}).encode())
        self.assertEqual(self.hc._state()["league2"]["difficultyselect"], 12)
        self.set_level(20)
        self.assertEqual(self.hc.l2_me(self.hc._state())["difficultybest"], 19)

    def test_perks_by_level(self):
        me = self.hc.coach_me(self.hc._state(), 0)
        self.assertFalse(me["igr"])
        self.assertEqual(me["vipDetail"], 0)
        keys = [s["key"] for s in self.hc.coach_scouters(self.hc._state(), 0)]
        self.assertEqual(keys, ["default_A01", "default_B01"])
        self.set_level(50)
        me = self.hc.coach_me(self.hc._state(), 0)
        self.assertTrue(me["igr"])
        self.assertGreater(me["vipDetail"], 0)
        self.assertEqual(len(self.hc.coach_scouters(self.hc._state(), 0)), 4)

    def test_sale_fee_discount_by_level(self):
        o = {"price": 100000, "completefee": {"base": 10000}}
        self.assertEqual(self.hc.sale_net(o), 90000)
        self.set_level(20)
        self.assertEqual(self.hc.sale_net(o), 92000)
        self.set_level(50)
        self.assertEqual(self.hc.sale_net(o), 95000)

    def test_locked_scout_refused(self):
        out = J(self.hc.ep_trade3_proposal("", json.dumps({"id": "vip", "playerids": []}).encode()))
        self.assertFalse(out["result"])

    def season(self, play_rounds):
        """Start a league season at level 12, play `play_rounds` of my matches (draws), simulate
        the rest, end it; returns (season reply, EP gained at the end)."""
        hc = self.hc
        hc.ep_l2_calendar("", json.dumps({"difficulty": 12, "sponsor": "1"}).encode())
        st = hc._state(); me = hc.my_teamid(st); teams = st["league2"]["league"]["teams"]
        for rnd in range(st["league2"]["league"]["maxround"] + 1):
            h, a = next((h, a) for h, a in hc.league_round(teams, rnd) if me in (h, a))
            req = json.dumps({"matchtype": "league", "playtype": "normal", "round": rnd, "home": h, "away": a}).encode()
            if rnd < play_rounds:
                mid = J(hc.ep_l2_match("", req))["resources"][0]["body"]["id"]
                hc.route(f"/match/{mid}/end")("", end_body(me, a if h == me else h, 1, 1))
            else:
                hc.ep_l2_match("", req, sim=True)
        ep0 = self.coach()["ep"]
        out = J(hc.ep_l2_end("", b""))
        return out, self.coach()["ep"] - ep0

    def test_simulated_season_pays_floor_share(self):
        out, gained = self.season(0)
        self.assertEqual(out["rewards"]["money"]["share"], 0.2)
        self.assertEqual(gained, out["rewards"]["money"]["reward"]["total"])

    def test_played_season_pays_full(self):
        out, gained = self.season(9)  # 9 of 18 = 50%
        self.assertEqual(out["rewards"]["money"]["share"], 1.0)
        self.assertEqual(gained, out["rewards"]["money"]["reward"]["total"])
        d = out["rewards"]["money"]["reward"]["detail"]
        self.assertEqual(sum(d.values()), out["rewards"]["money"]["reward"]["total"])
        self.assertLessEqual(out["promotion"]["next"], 12)  # level 1 coach: capped at league level 3
