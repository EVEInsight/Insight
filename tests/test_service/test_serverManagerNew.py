from tests.abstract import AsyncTesting, DatabaseTesting
from service import ServerManager
from tests.mocks.libDiscord.Guild import Guild
from tests.mocks.libDiscord.TextChannel import TextChannel
from tests.mocks.libDiscord.DMChannel import DMChannel
from tests.test_service import test_serverManagerLoaded
import random
import unittest


class TestServerManagerNew(test_serverManagerLoaded.TestServerManagerLoaded):
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
            prefixes = self.serverManager.default_prefixes
            self.assert_prefixes[i] = prefixes
            self.guilds.append(Guild(i))
            for t in range(0, random.randint(1, 10)):
                self.textChannels.append(TextChannel(random.randint(1, 25000), i))
        for i in range(0, 1000):
            self.directMessages.append(DMChannel(random.randint(1, 25000)))
        for i in self.textChannels:
            self.client.add_channel(i)

    @unittest.SkipTest
    def test__invalidate_prefixes(self):
        return

    @unittest.SkipTest
    def test_add_prefix(self):
        return
