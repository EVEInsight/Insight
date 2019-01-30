from tests.abstract import AsyncTesting
from discord_bot.discord_options import mapper_index, option_returns_object, option_calls_coroutine
from tests.mocks import DiscordInsightClient
from tests.mocks.libDiscord.TextChannel import TextChannel
from tests.mocks.libDiscord.Message import Message
from tests.mocks.libDiscord.User import User
import random
import InsightExc
import discord
import unittest


class TestMapperIndex(AsyncTesting.AsyncTesting):
    def setUp(self):
        super().setUp()
        self.client = DiscordInsightClient.DiscordInsightClient()
        message = Message(TextChannel(1, 1), User(1, "TestUser"), "This is the start of a command message.")
        self.options = mapper_index(self.client, message)
        self.counter = 0

    async def set_counter(self):
        self.counter = 55

    def test_set_main_header(self):
        header_str = "This is a header test string."
        self.options.set_main_header(header_str)
        self.assertEqual(header_str, self.options._header_text)

    def test_set_footer_text(self):
        footer_str = "This is a footer testing string."
        self.options.set_footer_text(footer_str)
        self.assertEqual(footer_str, self.options._footer_text)

    def test_add_blank_line(self):
        self.assertEqual(0, len(self.options._printout_format))
        self.options.add_blank_line()
        self.assertEqual(1, len(self.options._printout_format))

    def test_add_header_row(self):
        self.options.add_header_row("New header")
        self.assertEqual(1, len(self.options.e_header_container))
        self.assertEqual(0, self.options.header_index)
        self.options.add_header_row("New header 2")  # no body items so we overwrite tbe previous header
        self.assertEqual(1, len(self.options.e_header_container))
        self.assertEqual(0, self.options.header_index)
        with self.subTest("Adding body items"):
            self.options.add_option(option_returns_object("Item 1", "item", 1))
            self.options.add_header_row("Header 3")
            self.assertEqual(2, len(self.options.e_header_container))
            self.assertEqual(1, self.options.header_index)

    def test__current_option_index(self):
        self.assertEqual(0, self.options._current_option_index())
        self.options.add_header_row("Header")
        self.assertEqual(0, self.options._current_option_index())
        self.options.add_option(option_returns_object("Item 1", "item", 1))
        self.assertEqual(1, self.options._current_option_index())
        self.options.add_option(option_returns_object("Item 2", "item", 1))
        self.assertEqual(2, self.options._current_option_index())

    def test_set_bit_length(self):
        self.options.set_bit_length(16)
        self.assertEqual(16, self.options.maxbitlength)

    def test_add_option(self):
        for i in range(0, 401):
            if random.choice([True, False]):
                opt = option_returns_object("option", "desc", 1)
            else:
                opt = option_calls_coroutine("test coro", "test", None)
            self.options.add_option(opt)
            self.assertEqual(i+1, self.options._current_option_index())
            self.assertTrue(opt in self.options._option_container)
        with self.assertRaises(InsightExc.userInput.TooManyOptions):
            self.options.add_option(option_calls_coroutine("test coro", "test", None))

    def test_get_embed(self):  # todo add more interesting test cases
        self.assertIsInstance(self.options.get_embed(), discord.Embed)

    def test_check_conditions(self):
        self.options.add_option(option_returns_object("test", "", 1))
        self.loop.run_until_complete(self.options.check_conditions())

    def test_isInt(self):
        self.assertTrue(self.options.isInt("123"))
        self.assertFalse(self.options.isInt("123.12"))
        self.assertFalse(self.options.isInt("t"))

    def test_check_response(self):
        self.options.add_option(option_returns_object("Item", "", 5))
        for invalid_option in ["1", "2", "-1", "zero"]:
            with self.assertRaises(InsightExc.userInput.InvalidIndex):
                self.loop.run_until_complete(self.options.check_response(invalid_option))
        self.loop.run_until_complete(self.options.check_response("0"))

    @unittest.SkipTest
    def test_add_additional(self):
        self.fail()

    def test_get_option(self):
        opt = option_returns_object("1", "1", 1)
        self.options.add_option(opt)
        self.assertEqual(opt, self.options.get_option(0))

    def test_response_action(self):
        with self.subTest("Returns object"):
            self.options.add_option(option_returns_object("1", "", 5))
            self.assertEqual(5, self.loop.run_until_complete(self.options.response_action("0")))
        with self.subTest("Calls coro"):
            self.assertEqual(0, self.counter)
            self.options.add_option(option_calls_coroutine("1", "", self.set_counter()))
            self.loop.run_until_complete(self.options.response_action("1"))
            self.assertEqual(55, self.counter)

    def test_name(self):
        self.assertEqual("Option Selection", self.options.name())
