from tests.abstract import AsyncTesting, DatabaseTesting
from service import ServerManager
from tests.mocks.libDiscord.Guild import Guild
from tests.mocks.libDiscord.TextChannel import TextChannel
from tests.mocks.libDiscord.DMChannel import DMChannel
import random


class TestServerManagerLoaded(AsyncTesting.AsyncTesting, DatabaseTesting.DatabaseTesting):
    def setUp(self):
        AsyncTesting.AsyncTesting.setUp(self)
        self.resources = None
        DatabaseTesting.DatabaseTesting.setUp(self)
        self.serverManager = ServerManager(self.service, self.client)
        self.guilds = []
        self.textChannels = []
        self.directMessages = []
        for i in range(0, 1000):
            self.serverManager.guild_prefixes[i] = self.serverManager.default_prefixes + [self.random_string(2)]
            self.guilds.append(Guild(i))
            for t in range(0, random.randint(1, 10)):
                self.textChannels.append(TextChannel(random.randint(1, 25000), i))
        for i in range(0, 1000):
            self.directMessages.append(DMChannel(random.randint(1, 25000)))

    def test__invalidate_prefixes(self):
        for i in range(0, 1000):
            with self.subTest(id=i):
                self.assertIsInstance(self.serverManager.guild_prefixes.get(i), list)
                self.loop.run_until_complete(self.serverManager._invalidate_prefixes(Guild(i)))
                self.assertEqual(self.serverManager.guild_prefixes.get(i), None)

    def test_get_min_prefix_textChannel(self):
        for i in self.textChannels:
            with self.subTest(TextChannel=i.id):
                min_pref = self.loop.run_until_complete(self.serverManager.get_min_prefix(i))
                self.assertTrue(len(min_pref), 1)
                self.assertTrue(min_pref in self.serverManager.default_prefixes)

    def test_get_min_prefix_DM(self):
        for i in self.directMessages:
            with self.subTest(TextChannel=i.id):
                min_pref = self.loop.run_until_complete(self.serverManager.get_min_prefix(i))
                self.assertTrue(len(min_pref), 1)
                self.assertTrue(min_pref in self.serverManager.default_prefixes)


    # def test__get_append_self_prefix(self):
    #     self.fail()
    #
    # def test_get_server_prefixes(self):
    #     self.fail()
    #
    # def test__get_prefixes_from_db(self):
    #     self.fail()
    #
    # def test_add_prefix(self):
    #     self.fail()
    #
    # def test_remove_prefix(self):
    #     self.fail()
    #
    # def test__add_prefix(self):
    #     self.fail()
    #
    # def test__remove_prefix(self):
    #     self.fail()
    #
    # def test_populate_guilds(self):
    #     self.fail()
    #
    # def test_loader(self):
    #     self.fail()
