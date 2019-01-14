from unittest import TestCase
from tests.resources import ResourceRoot
from InsightUtilities import InsightCommands
import asyncio
import os
import random
import string
import InsightExc
import datetime


class TestInsightCommands(TestCase):
    def setUp(self):
        self.resources = os.path.join(ResourceRoot.ResourceRoot.get_path(), 'InsightUtilities', 'InsightCommands')
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.commands = InsightCommands()
        asyncio.set_event_loop(None)
        self.prefixes = ['!', '?']
        self.value_called = None

    async def helper_parse_and_run_set(self, val):
        self.value_called = val

    def helper_parse_and_run_coro(self, command_str):
        self.loop.run_until_complete(self.commands.parse_and_run(1, self.prefixes, command_str,
                                                                 about=self.helper_parse_and_run_set("about"),
                                                                 admin=self.helper_parse_and_run_set("admin"),
                                                                 create=self.helper_parse_and_run_set("create"),
                                                                 dscan=self.helper_parse_and_run_set("dscan"),
                                                                 eightball=self.helper_parse_and_run_set("8ball"),
                                                                 help=self.helper_parse_and_run_set("help"),
                                                                 lock=self.helper_parse_and_run_set("lock"),
                                                                 prefix=self.helper_parse_and_run_set("prefix"),
                                                                 quit=self.helper_parse_and_run_set("quit"),
                                                                 remove=self.helper_parse_and_run_set("remove"),
                                                                 settings=self.helper_parse_and_run_set("settings"),
                                                                 start=self.helper_parse_and_run_set("start"),
                                                                 status=self.helper_parse_and_run_set("status"),
                                                                 stop=self.helper_parse_and_run_set("stop"),
                                                                 sync=self.helper_parse_and_run_set("sync"),
                                                                 unlock=self.helper_parse_and_run_set("unlock")))

    def test_parse_and_run(self):
        raise_count = 0
        for c in ["{}about", "{}admin", "{}create", "{}dscan", "{}8ball", "{}help", "{}lock", "{}prefix",
                  "{}quit", "{}remove", "{}settings", "{}start", "{}status", "{}stop", "{}sync", "{}unlock"]:
            invalid_command_str = c.format('!' + random.choice(string.ascii_letters))
            for p in self.prefixes:
                command_str = c.format(p)
                with self.subTest(commannd=command_str):
                    self.helper_parse_and_run_coro(command_str)
                    self.assertEqual(self.value_called, c.format(''))
                    if raise_count == 0:
                        self.assertEqual(self.commands.notfound_timers.get(1), None)
                    else:
                        self.assertIsInstance(self.commands.notfound_timers.get(1), datetime.datetime)
            with self.subTest(commannd=invalid_command_str):
                if raise_count == 0:
                    self.assertEqual(self.commands.notfound_timers.get(1), None)
                    self.assertRaises(InsightExc.userInput.CommandNotFound, self.helper_parse_and_run_coro, invalid_command_str)
                    raise_count += 1
                else:
                    self.helper_parse_and_run_coro(invalid_command_str)
                    self.assertIsInstance(self.commands.notfound_timers.get(1), datetime.datetime)

    def test_is_command(self):
        for s in self.helper_file_lines('valid_prefixes.txt'):
            with self.subTest(command=s, valid=True):
                self.assertTrue(self.commands.is_command(self.prefixes, s))
        for s in self.helper_file_lines('invalid_prefixes.txt'):
            with self.subTest(command=s, valid=False):
                self.assertFalse(self.commands.is_command(self.prefixes, s))
        with self.subTest(command="", valid=True):
            self.assertFalse(self.commands.is_command(self.prefixes, ""))

    def test_strip_prefix(self):
        pass

    def test_strip_non_command(self):
        pass

    def test_can_raise_notfound(self):
        pass

    def test_raise_notfound(self):
        pass

    def helper_file_lines(self, filename):
        with open(os.path.join(self.resources, filename)) as f:
            return f.read().splitlines()
