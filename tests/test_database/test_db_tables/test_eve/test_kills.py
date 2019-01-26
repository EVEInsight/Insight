from tests.abstract import DatabaseTesting
from database.db_tables import tb_kills, tb_attackers, tb_victims, tb_systems, tb_types, tb_locations, tb_groups, tb_constellations, tb_regions, tb_categories, name_resolver
from database.db_tables.filters import tb_Filter_characters, tb_Filter_corporations, tb_Filter_alliances, tb_Filter_types, tb_Filter_groups, tb_Filter_systems, tb_Filter_constellations, tb_Filter_regions
import datetime
import unittest
from tests.mocks import ServiceModule


class TestKills(DatabaseTesting.DatabaseTesting):
    def setUp(self):
        super().setUp()
        self.service = ServiceModule.ServiceModule(self.db)
        self.set_resource_path('db_tables', 'eve', 'mails')
        self.data = self.file_json("74647898.json")
        tb_kills.make_row(self.data.get("package"), self.service)
        self.km: tb_kills = tb_kills.get_row(self.data.get("package"), self.service)

    def test_load_fk_objects(self):
        self.tearDown()
        super().setUp()
        self.set_resource_path('db_tables', 'eve', 'mails')
        data = self.file_json("74647898.json")
        row = tb_kills(data.get("package"))
        row.load_fk_objects()
        self.db.merge(row)
        self.db.commit()
        row = tb_kills.get_row(data.get("package"), self.service)
        self.assertIsInstance(row.object_system, tb_systems)
        self.assertIsInstance(row.object_location, tb_locations)
        self.assertIsInstance(row.object_victim, tb_victims)
        self.assertIsInstance(row.object_attackers, list)
        self.assertEqual(27, len(row.object_attackers))

    def test_compare_value(self):
        return  # not used function

    def test_primary_key_row(self):
        self.assertEqual(tb_kills.kill_id, tb_kills.primary_key_row())

    def test_make_row(self):
        self.tearDown()
        super().setUp()
        self.set_resource_path('db_tables', 'eve', 'mails')
        data = self.file_json("74647898.json")
        with self.subTest("Insert initial."):
            self.assertIsInstance(tb_kills.make_row(data.get("package"), self.service), tb_kills)
        with self.subTest("Insert duplicate."):
            self.assertEqual(None, tb_kills.make_row(data.get("package"), self.service))
        with self.subTest("Insert invalid json."):
            self.assertEqual(None, tb_kills.make_row(data, self.service))

    def test_get_row(self):
        self.assertIsInstance(tb_kills.get_row(self.data.get("package"), self.service), tb_kills)

    def test_get_au_location_distance(self):
        loc_nearest = tb_locations(40181682)
        loc_nearest.pos_x = -268292939299
        loc_nearest.pos_y = -31101911311
        loc_nearest.pos_z = 361046068690
        self.db.merge(loc_nearest)
        self.db.commit()
        self.km = tb_kills.get_row(self.data.get("package"), self.service)
        self.assertEqual(7.86165310033881e-05, self.km.get_au_location_distance())

    def helper_filter_loss(self, f_contains, f_missing):
        with self.subTest("blacklist"):
            self.assertFalse(self.km.filter_loss(f_contains, using_blacklist=True))
            self.assertTrue(self.km.filter_loss(f_missing, using_blacklist=True))
        with self.subTest("whitelist"):
            self.assertTrue(self.km.filter_loss(f_contains, using_blacklist=False))
            self.assertFalse(self.km.filter_loss(f_missing, using_blacklist=False))

    def test_filter_loss_character(self):
        f_contains = [tb_Filter_characters(i, 1, False) for i in [700976878, 2114664129]]
        f_missing = [tb_Filter_characters(i, 1, False) for i in [2114664129, 94274201]]
        self.helper_filter_loss(f_contains, f_missing)

    def test_filter_loss_corporation(self):
        f_contains = [tb_Filter_corporations(i, 1, False) for i in [109788662, 98410772]]
        f_missing = [tb_Filter_corporations(i, 1, False) for i in [98410772, 98388312]]
        self.helper_filter_loss(f_contains, f_missing)

    def test_filter_loss_alliance(self):
        f_contains = [tb_Filter_alliances(i, 1, False) for i in [1354830081, 99005338]]
        f_missing = [tb_Filter_alliances(i, 1, False) for i in [1727758877, 99005338]]
        self.helper_filter_loss(f_contains, f_missing)

    def test_filter_loss_type(self):
        f_contains = [tb_Filter_types(i, 1, False) for i in [11965, 11186]]
        f_missing = [tb_Filter_types(i, 1, False) for i in [11202, 34828]]
        self.helper_filter_loss(f_contains, f_missing)

    def test_filter_loss_groups(self):
        self.db.add(tb_groups(833))
        self.db.add(tb_groups(831))
        self.db.commit()
        tb_groups.api_mass_data_resolve(self.service)
        self.km = tb_kills.get_row(self.data.get("package"), self.service)
        f_contains = [tb_Filter_groups(i, 1, False) for i in [833, 831]]
        f_missing = [tb_Filter_groups(i, 1, False) for i in [831, 10830]]
        self.helper_filter_loss(f_contains, f_missing)

    def test_filter_system_ly(self):
        nearby = tb_Filter_systems(30002871, 1)
        nearby.max = 7.0
        jita = tb_Filter_systems(30000142, 1)
        jita.max = 10.0
        jan = tb_Filter_systems(30001385, 1)
        jan.max = 10.0
        self.db.merge(nearby)
        self.db.merge(jita)
        self.db.merge(jan)
        self.db.commit()
        tb_systems.api_mass_data_resolve(self.service)
        self.km = tb_kills.get_row(self.data.get("package"), self.service)
        nearby = tb_Filter_systems.get_row(1, 30002871, self.service)
        jita = tb_Filter_systems.get_row(1, 30000142, self.service)
        jan = tb_Filter_systems.get_row(1, 30001385, self.service)
        f_contains = [nearby, jita]
        f_missing = [jita, jan]
        with self.subTest("blacklist"):
            self.assertEqual(None, self.km.filter_system_ly(f_contains, using_blacklist=True))
            self.assertEqual(self.km.object_system, self.km.filter_system_ly(f_missing, using_blacklist=True))
        with self.subTest("whitelist"):
            self.assertEqual(nearby.object_item, self.km.filter_system_ly(f_contains, using_blacklist=False))
            self.assertEqual(None, self.km.filter_system_ly(f_missing, using_blacklist=False))

    @unittest.SkipTest
    def test_filter_system_gates(self):  # todo
        self.fail()

    def helper_filter_system(self, f_contains, f_missing):
        with self.subTest("blacklist"):
            self.assertEqual(None, self.km.filter_system(f_contains, using_blacklist=True))
            self.assertEqual(self.km.object_system, self.km.filter_system(f_missing, using_blacklist=True))
        with self.subTest("whitelist"):
            if isinstance(f_contains[0], tb_Filter_constellations):
                self.assertEqual(self.km.object_system.object_constellation, self.km.filter_system(f_contains, using_blacklist=False))
            elif isinstance(f_contains[0], tb_Filter_regions):
                self.assertEqual(self.km.object_system.object_constellation.object_region, self.km.filter_system(f_contains, using_blacklist=False))
            else:
                self.assertEqual(self.km.object_system, self.km.filter_system(f_contains, using_blacklist=False))
            self.assertEqual(None, self.km.filter_system(f_missing, using_blacklist=False))

    def test_filter_system_system(self):
        self.db.merge(tb_Filter_systems(30000142, 1))
        self.db.merge(tb_Filter_systems(30002868, 1))
        self.db.commit()
        f_contains = [tb_Filter_systems.get_row(1, 30002868, self.service)]
        f_missing = [tb_Filter_systems.get_row(1, 30000142, self.service)]
        self.helper_filter_system(f_contains, f_missing)

    def test_filter_system_constellation(self):
        self.db.merge(tb_Filter_constellations(20000421, 1))
        self.db.merge(tb_Filter_systems(20000020, 1))
        self.db.commit()
        tb_constellations.api_mass_data_resolve(self.service)
        self.km = tb_kills.get_row(self.data.get("package"), self.service)
        f_contains = [tb_Filter_constellations.get_row(1, 20000421, self.service)]
        f_missing = [tb_Filter_constellations.get_row(1, 20000020, self.service)]
        self.helper_filter_system(f_contains, f_missing)

    def test_filter_system_region(self):
        self.db.merge(tb_Filter_regions(10000034, 1))
        self.db.merge(tb_Filter_regions(10000002, 1))
        self.db.commit()
        tb_regions.api_mass_data_resolve(self.service)
        tb_constellations.api_mass_data_resolve(self.service)
        self.km = tb_kills.get_row(self.data.get("package"), self.service)
        f_contains = [tb_Filter_regions.get_row(1, 10000034, self.service)]
        f_missing = [tb_Filter_regions.get_row(1, 10000002, self.service)]
        self.helper_filter_system(f_contains, f_missing)

    def test_filter_attackers_character(self):
        f_contains = [tb_Filter_characters(i, 1, False) for i in [375279210, 2112908361, 10]]
        f_missing = [tb_Filter_characters(i, 1, False) for i in [1326083433, 1363013499]]
        with self.subTest("blacklist-contains"):
            response = self.km.filter_attackers(self.km.object_attackers, f_contains, using_blacklist=True)
            self.assertEqual(25, len(response))
            for i in response:
                self.assertTrue(i.character_id not in [f.filter_id for f in f_contains])
        with self.subTest("blacklist-missing"):
            response = self.km.filter_attackers(self.km.object_attackers, f_missing, using_blacklist=True)
            self.assertEqual(27, len(response))
            for i in response:
                self.assertTrue(i.character_id not in [f.filter_id for f in f_missing])
        with self.subTest("whitelist-contains"):
            response = self.km.filter_attackers(self.km.object_attackers, f_contains, using_blacklist=False)
            self.assertEqual(2, len(response))
            for i in response:
                self.assertTrue(i.character_id in [f.filter_id for f in f_contains])
        with self.subTest("whitelist-missing"):
            response = self.km.filter_attackers(self.km.object_attackers, f_missing, using_blacklist=False)
            self.assertEqual(0, len(response))

    def test_filter_attackers_corporation(self):
        f_contains = [tb_Filter_corporations(i, 1, False) for i in [98558506, 98582593]]
        f_missing = [tb_Filter_corporations(i, 1, False) for i in [761955047, 1673385956]]
        with self.subTest("blacklist-contains"):
            response = self.km.filter_attackers(self.km.object_attackers, f_contains, using_blacklist=True)
            self.assertEqual(11, len(response))
            for i in response:
                self.assertTrue(i.corporation_id not in [f.filter_id for f in f_contains])
        with self.subTest("blacklist-missing"):
            response = self.km.filter_attackers(self.km.object_attackers, f_missing, using_blacklist=True)
            self.assertEqual(27, len(response))
            for i in response:
                self.assertTrue(i.corporation_id not in [f.filter_id for f in f_missing])
        with self.subTest("whitelist-contains"):
            response = self.km.filter_attackers(self.km.object_attackers, f_contains, using_blacklist=False)
            self.assertEqual(16, len(response))
            for i in response:
                self.assertTrue(i.corporation_id in [f.filter_id for f in f_contains])
        with self.subTest("whitelist-missing"):
            response = self.km.filter_attackers(self.km.object_attackers, f_missing, using_blacklist=False)
            self.assertEqual(0, len(response))

    def test_filter_attackers_alliance(self):
        f_contains = [tb_Filter_alliances(i, 1, False) for i in [99005338, 1727758877]]
        f_missing = [tb_Filter_alliances(i, 1, False) for i in [1727758877, 498125261]]
        with self.subTest("blacklist-contains"):
            response = self.km.filter_attackers(self.km.object_attackers, f_contains, using_blacklist=True)
            self.assertEqual(0, len(response))
        with self.subTest("blacklist-missing"):
            response = self.km.filter_attackers(self.km.object_attackers, f_missing, using_blacklist=True)
            self.assertEqual(27, len(response))
            for i in response:
                self.assertTrue(i.alliance_id not in [f.filter_id for f in f_missing])
        with self.subTest("whitelist-contains"):
            response = self.km.filter_attackers(self.km.object_attackers, f_contains, using_blacklist=False)
            self.assertEqual(27, len(response))
            for i in response:
                self.assertTrue(i.alliance_id in [f.filter_id for f in f_contains])
        with self.subTest("whitelist-missing"):
            response = self.km.filter_attackers(self.km.object_attackers, f_missing, using_blacklist=False)
            self.assertEqual(0, len(response))

    def helper_filter_victim(self, f_contains, f_missing):
        with self.subTest("blacklist"):
            self.assertEqual(None, self.km.filter_victim(self.km.object_victim, f_contains, using_blacklist=True))
            self.assertEqual(self.km.object_victim, self.km.filter_victim(self.km.object_victim, f_missing, using_blacklist=True))
        with self.subTest("whitelist"):
            self.assertEqual(self.km.object_victim, self.km.filter_victim(self.km.object_victim, f_contains, using_blacklist=False))
            self.assertEqual(None, self.km.filter_victim(self.km.object_victim, f_missing, using_blacklist=False))

    def test_filter_victim_character(self):
        f_contains = [tb_Filter_characters(i, 1, False) for i in [700976878, 2114664129]]
        f_missing = [tb_Filter_characters(i, 1, False) for i in [2114664129, 94274201]]
        self.helper_filter_victim(f_contains, f_missing)

    def test_filter_victim_corporation(self):
        f_contains = [tb_Filter_corporations(i, 1, False) for i in [109788662, 98410772]]
        f_missing = [tb_Filter_corporations(i, 1, False) for i in [98410772, 98388312]]
        self.helper_filter_victim(f_contains, f_missing)

    def test_filter_victim_alliance(self):
        f_contains = [tb_Filter_alliances(i, 1, False) for i in [1354830081, 99005338]]
        f_missing = [tb_Filter_alliances(i, 1, False) for i in [1727758877, 99005338]]
        self.helper_filter_victim(f_contains, f_missing)

    def test_filter_victim_type(self):
        f_contains = [tb_Filter_types(i, 1, False) for i in [11965, 11186]]
        f_missing = [tb_Filter_types(i, 1, False) for i in [11202, 34828]]
        self.helper_filter_victim(f_contains, f_missing)

    def test_get_final_blow(self):
        row = self.km.get_final_blow()
        self.assertIsInstance(row, tb_attackers)
        self.assertEqual(375279210, row.character_id)

    def test_get_victim(self):
        row = self.km.get_victim()
        self.assertIsInstance(row, tb_victims)
        self.assertEqual(700976878, row.character_id)
        self.assertEqual(109788662, row.corporation_id)
        self.assertEqual(1354830081, row.alliance_id)

    def test_get_system(self):
        row = self.km.get_system()
        self.assertIsInstance(row, tb_systems)
        self.assertEqual(30002868, row.system_id)

    def test_get_highest_attacker(self):
        tb_types.update_prices(self.service)
        with self.subTest("All"):
            row = self.km.get_highest_attacker(self.km.object_attackers)
            self.assertIsInstance(row, tb_attackers)
            self.assertEqual(90090542, row.character_id)
            self.assertEqual(37480, row.ship_type_id)
        with self.subTest("Subset"):
            subset = []
            for i in self.km.object_attackers:
                if i.corporation_id == 98477766:  # vanguard subset
                    subset.append(i)
            row = self.km.get_highest_attacker(subset)
            self.assertIsInstance(row, tb_attackers)
            self.assertEqual(2112908361, row.character_id)
            self.assertEqual(34828, row.ship_type_id)

    def test_get_alive_nonnpc_count(self):
        for group_id in [1305, 833, 831, 893, 1527, 25, 1534]:
            self.db.add(tb_groups(group_id))
        self.db.commit()
        tb_groups.api_mass_data_resolve(self.service)
        self.km = tb_kills.get_row(self.data.get("package"), self.service)
        self.assertEqual(27, self.km.get_alive_nonnpc_count(self.km.object_attackers))

    def test_get_time(self):
        time = self.km.get_time()
        self.assertIsInstance(time, datetime.datetime)
        self.assertEqual(datetime.datetime(2019, 1, 18, 0, 34, 23), time)

    def test_str_eve_time(self):
        with self.subTest("include_date=True"):
            self.assertEqual("18.01.2019 00:34", self.km.str_eve_time(include_date=True))
        with self.subTest("include_date=False"):
            self.assertEqual("00:34", self.km.str_eve_time(include_date=False))

    def test_str_zk_link(self):
        self.assertEqual("https://zkillboard.com/kill/74647898/", self.km.str_zk_link())

    def test_str_location_zk(self):
        self.assertEqual("https://zkillboard.com/location/40181682/", self.km.str_location_zk())

    def test_str_total_involved(self):
        self.assertEqual("27", self.km.str_total_involved())

    def test_str_damage(self):
        self.assertEqual("9,271", self.km.str_damage())

    def test_str_isklost(self):
        self.assertEqual("316.4m", self.km.str_isklost())

    def test_str_attacker_count(self):
        base = self.km.object_attackers
        with self.subTest("solo"):
            self.km.object_attackers = base[:1]
            self.assertEqual("solo", self.km.str_attacker_count())
        with self.subTest("1 other"):
            self.km.object_attackers = base[:2]
            self.assertEqual("and **1** other", self.km.str_attacker_count())
        with self.subTest("plural"):
            self.km.object_attackers = base
            self.assertEqual("and **26** others", self.km.str_attacker_count())

    def test_str_minutes_ago(self):
        with self.subTest("Less that a minute"):
            self.km.killmail_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
            self.assertEqual("10 s/ago", self.km.str_minutes_ago())
            self.assertEqual("10 seconds ago", self.km.str_minutes_ago(text_ago=True))
        with self.subTest("More that a minute"):
            self.km.killmail_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=64)
            self.assertEqual("1.1 m/ago", self.km.str_minutes_ago())
            self.assertEqual("1.1 minutes ago", self.km.str_minutes_ago(text_ago=True))

    def test_str_ly_range(self):
        self.db.add(tb_systems(30000142))
        self.db.commit()
        tb_systems.api_mass_data_resolve(self.service)
        updated_km = tb_kills.get_row(self.data.get("package"), self.service)
        updated_system = tb_systems.get_row(30000142, self.service)
        self.assertEqual("27.6", updated_km.str_ly_range(updated_system))
        self.assertEqual("0.0", updated_km.str_ly_range(updated_km.object_system))

    def test_str_location_name(self):
        loc_nearest = tb_locations(40181682)
        loc_nearest.name = "9-0QB7 IV"
        loc_nearest.pos_x = -268292939299
        loc_nearest.pos_y = -31101911311
        loc_nearest.pos_z = 361046068690
        self.db.merge(loc_nearest)
        self.db.commit()
        self.km = tb_kills.get_row(self.data.get("package"), self.service)
        with self.subTest("name_only=True, on grid"):
            self.assertEqual("9-0QB7 IV", self.km.str_location_name(name_only=True))
        with self.subTest("name_only=False, on grid"):
            self.assertEqual(" near **9-0QB7 IV**.", self.km.str_location_name(name_only=False))
        self.km.object_victim.pos_x += 500000000000
        with self.subTest("name_only=True, off grid"):
            self.assertEqual("9-0QB7 IV (3.3 AU)", self.km.str_location_name(name_only=True))
        with self.subTest("name_only=False, off grid"):
            self.assertEqual(" near **9-0QB7 IV (3.3 AU)**.", self.km.str_location_name(name_only=False))

    @unittest.SkipTest
    def test_str_overview(self):  # todo
        self.fail()

    def test_to_dict(self):
        d = self.km.to_jsonDictionary()
        self.tearDown()
        DatabaseTesting.DatabaseTesting.setUp(self)
        new = tb_kills.make_row(d.get("package"), self.service)
        self.assertEqual(d, new.to_jsonDictionary())
