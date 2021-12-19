from tests.abstract import AsyncTesting, DatabaseTesting
from service import ServerManager
from tests.mocks.libDiscord.Guild import Guild
from tests.mocks.libDiscord.TextChannel import TextChannel
from tests.mocks.libDiscord.DMChannel import DMChannel
from database.db_tables.discord import tb_server_prefixes, tb_servers
import random


class TestServerManagerLoaded(AsyncTesting.AsyncTesting, DatabaseTesting.DatabaseTesting):
    """Test with all prefixes already loaded and existing in the database."""
    def setUp(self):
        AsyncTesting.AsyncTesting.setUp(self)
        self.resources = None
        DatabaseTesting.DatabaseTesting.setUp(self)
        self.serverManager = ServerManager(self.service, self.client)
        self.guilds = []
        self.textChannels = []
        self.directMessages = []
        self.assert_prefixes = {}
        for i in range(1, 100):
            prefixes = self.serverManager.default_prefixes + [self.random_string(1, 8, True)]
            self.serverManager.guild_prefixes[i] = prefixes
            self.assert_prefixes[i] = prefixes
            self.guilds.append(Guild(i))
            for t in range(0, random.randint(1, 10)):
                self.textChannels.append(TextChannel(random.randint(1, 25000), i))
            self.db.add(tb_servers(i))
            for p in prefixes:
                self.db.add(tb_server_prefixes(i, p, False))
            self.db.commit()
        for i in range(0, 1000):
            self.directMessages.append(DMChannel(random.randint(1, 25000)))
        for i in self.textChannels:
            self.client.add_channel(i)

    def tearDown(self):
        AsyncTesting.AsyncTesting.tearDown(self)
        DatabaseTesting.DatabaseTesting.tearDown(self)

    def test__invalidate_prefixes(self):
        for g in self.guilds:
            with self.subTest(id=g.id):
                self.assertIsInstance(self.serverManager.guild_prefixes.get(g.id), list)
                self.loop.run_until_complete(self.serverManager._invalidate_prefixes(g))
                self.assertEqual(self.serverManager.guild_prefixes.get(g.id), None)

    def test_get_min_prefix_textChannel(self):
        for i in self.textChannels:
            with self.subTest(TextChannel=i.id):
                min_pref = self.loop.run_until_complete(self.serverManager.get_min_prefix(i))
                self.assertEqual(len(min_pref), 1)
                self.assertTrue(min_pref in self.assert_prefixes.get(i.guild_id))

    def test_get_min_prefix_DM(self):
        for i in self.directMessages:
            with self.subTest(TextChannel=i.id):
                min_pref = self.loop.run_until_complete(self.serverManager.get_min_prefix(i))
                self.assertEqual(len(min_pref), 1)
                self.assertTrue(min_pref in self.serverManager.default_prefixes)

    def test__get_append_self_prefix_unset(self):
        for prefixes in self.assert_prefixes.values():
            with self.subTest(prefixes=str(prefixes)):
                resp = self.serverManager._get_append_self_prefix(prefixes)
                for a in prefixes:
                    self.assertTrue(a in resp)
                if len(self.serverManager.prefix_self) != 0:
                    self.assertTrue("@Insight" in resp)
                    self.assertEqual(len(prefixes) + 1, len(resp))
                else:
                    self.assertEqual(len(prefixes), len(resp))

    def test__get_append_self_prefix_set(self):
        self.serverManager.prefix_self = ["@Insight"]
        self.test__get_append_self_prefix_unset()

    def test_get_server_prefixes_textChannel_loaded(self):
        for tc in self.textChannels:
            with self.subTest(id=tc.id):
                assert_prefixes = self.assert_prefixes.get(tc.guild_id)
                resp = self.loop.run_until_complete(self.serverManager.get_server_prefixes(tc))
                for p in assert_prefixes:
                    self.assertTrue(p in resp)
                if len(self.serverManager.prefix_self) != 0:
                    self.assertTrue("@Insight" in resp)
                    self.assertEqual(len(assert_prefixes) + 2, len(resp))
                else:
                    self.assertEqual(len(assert_prefixes), len(resp))

    def test_get_server_prefixes_textChannel_unloaded(self):
        self.serverManager.guild_prefixes = {}
        self.test_get_server_prefixes_textChannel_loaded()

    def test_get_server_prefixes_DM_unloaded(self):
        self.serverManager.prefix_self = []
        for d in self.directMessages:
            with self.subTest(id=d.id):
                resp = self.loop.run_until_complete(self.serverManager.get_server_prefixes(d))
                self.assertEqual(self.serverManager.default_prefixes, resp)
        self.serverManager.prefix_self = [self.client.user.mention]
        for d in self.directMessages:
            with self.subTest(id=d.id):
                resp = self.loop.run_until_complete(self.serverManager.get_server_prefixes(d))
                self.assertEqual([self.client.user.mention] + self.serverManager.default_prefixes, resp)

    def test__get_prefixes_from_db(self):
        for g in self.guilds:
            with self.subTest(guild=g.id):
                assert_p = self.assert_prefixes.get(g.id)
                resp = self.serverManager._get_prefixes_from_db(g)
                self.assertEqual(len(resp), len(assert_p))
                for p in assert_p:
                    self.assertTrue(p in resp)

    def test_add_prefix(self):
        for g in self.guilds:
            with self.subTest(guild=g.id):
                assert_prefixes = set(self.assert_prefixes.get(g.id))
                for i in range(0, random.randint(1, 3)):
                    new_pref = self.random_string(1, 10, True)
                    assert_prefixes.add(new_pref)
                    self.loop.run_until_complete(self.serverManager.add_prefix(new_pref, g))
                prefixes = self.loop.run_until_complete(self.serverManager.get_server_prefixes(TextChannel(1, g.id)))
                self.assertEqual(len(prefixes), len(assert_prefixes))
                for p in prefixes:
                    self.assertTrue(p in assert_prefixes)

    def test_remove_prefix(self):
        for g in self.guilds:
            with self.subTest(guild=g.id):
                assert_prefixes = self.assert_prefixes.get(g.id)
                for p in assert_prefixes:
                    assert_prefixes.remove(p)
                    self.loop.run_until_complete(self.serverManager.remove_prefix(p, g))
                    pref = self.loop.run_until_complete(self.serverManager.get_server_prefixes(TextChannel(1, g.id)))
                    self.assertEqual(len(pref), len(assert_prefixes))
                    for p in assert_prefixes:
                        self.assertTrue(p in assert_prefixes)

    def test__add_prefix(self):
        return

    def test__remove_prefix(self):
        return

    def test_populate_guilds(self):
        self.serverManager.guild_prefixes = {}
        self.loop.run_until_complete(self.serverManager.populate_guilds())
        self.test_get_server_prefixes_textChannel_loaded()

    def test_loader(self):
        self.serverManager.guild_prefixes = {}
        self.loop.run_until_complete(self.serverManager.loader())
        self.test_get_server_prefixes_textChannel_loaded()
