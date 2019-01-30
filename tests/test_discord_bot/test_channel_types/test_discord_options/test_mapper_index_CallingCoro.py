from discord_bot.discord_options import mapper_index, option_returns_object, option_calls_coroutine
from tests.mocks.libDiscord.TextChannel import TextChannel
from tests.mocks.libDiscord.Message import Message
from tests.mocks.libDiscord.User import User
import InsightExc
import asyncio
from tests.abstract.TestCases.AbstractBotReplyTesting import AbstractBotReplyTesting


class TestMapperIndexCallingCoro(AbstractBotReplyTesting):
    def setUp(self):
        super().setUp()
        message = Message(TextChannel(1, 1), User(1, "TestUser"), "This is the start of a command message.")
        self.options = mapper_index(self.client, message, timeout_seconds=20)
        for i in range(0, 20):
            self.options.add_option(option_calls_coroutine("{}".format(i), "", self.helper_set_counter(i)))
        self.value = 0

    async def helper_set_counter(self, new_val):
        self.value = new_val

    def test_call_1(self):
        self.messageEmulator.respond_to_bot("1")
        self.helper_future_run_call(self.options())
        self.assertEqual(1, self.value)

    def test_call_invalid_index(self):
        for i in [-1, -2, 44, 10000]:
            with self.subTest(input=i):
                with self.assertRaises(InsightExc.userInput.InvalidIndex):
                    self.messageEmulator.respond_to_bot(str(i))
                    self.helper_future_run_call(self.options())
