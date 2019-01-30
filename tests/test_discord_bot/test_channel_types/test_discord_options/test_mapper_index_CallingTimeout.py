from tests.abstract import AsyncTesting
from discord_bot.discord_options import mapper_index, option_returns_object, option_calls_coroutine
from tests.mocks import DiscordInsightClient
from tests.mocks.libDiscord.TextChannel import TextChannel
from tests.mocks.libDiscord.Message import Message
from tests.mocks.libDiscord.User import User
import InsightExc


class TestMapperIndexCallingTimeout(AsyncTesting.AsyncTesting):
    def setUp(self):
        super().setUp()
        self.client = DiscordInsightClient.DiscordInsightClient()
        message = Message(TextChannel(1, 1), User(1, "TestUser"), "This is the start of a command message.")
        self.options = mapper_index(self.client, message, timeout_seconds=1)
        self.options.add_option(option_returns_object("1", "", 1))

    def test_call(self):
        with self.assertRaises(InsightExc.userInput.InputTimeout):
            self.loop.run_until_complete(self.options())
