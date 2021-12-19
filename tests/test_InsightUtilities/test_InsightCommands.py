from InsightUtilities import InsightCommands, InsightSingleton
import random
import string
import InsightExc
import datetime
from tests.abstract import AsyncTesting


class TestInsightCommands(AsyncTesting.AsyncTesting):
    def setUp(self):
        super().setUp()
        self.set_resource_path('InsightUtilities', 'InsightCommands')
        self.commands = InsightCommands()
        self.prefixes = ['!', '?']
        self.f_valid_prefixes = self.get_file_lines('valid_prefixes.txt')
        self.f_invalid = self.get_file_lines('invalid_prefixes.txt')
        self.value_called = None

    def tearDown(self):
        super().tearDown()
        InsightSingleton.clear_instance_references()

    async def helper_parse_and_run_set(self, val):
        self.value_called = val

    def helper_parse_and_run_coro(self, command_str):
        self.loop.run_until_complete(self.commands.parse_and_run(1, self.prefixes, command_str,
                                                                 about=self.helper_parse_and_run_set("about"),
                                                                 admin=self.helper_parse_and_run_set("admin"),
                                                                 create=self.helper_parse_and_run_set("create"),
                                                                 eightball=self.helper_parse_and_run_set("8ball"),
                                                                 help=self.helper_parse_and_run_set("help"),
                                                                 lock=self.helper_parse_and_run_set("lock"),
                                                                 lscan=self.helper_parse_and_run_set("dscan"),
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
                self.value_called = None
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
        for s in self.get_file_lines('valid_prefixes.txt'):
            with self.subTest(command=s, valid=True):
                self.assertTrue(self.commands.is_command(self.prefixes, s))
        for s in self.get_file_lines('invalid_prefixes.txt'):
            with self.subTest(command=s, valid=False):
                self.assertFalse(self.commands.is_command(self.prefixes, s))
        with self.subTest(command="", valid=False):
            self.assertFalse(self.commands.is_command(self.prefixes, ""))

    def test_strip_prefix(self):
        for c in self.iterate_assert_file('test_strip_prefix.txt', 'assert_strip_prefix.txt'):
            with self.subTest(command=c[0]):
                self.assertEqual(self.commands.strip_prefix(self.prefixes, c[0]), c[1])

    def test_strip_non_command(self):
        for c in self.iterate_assert_file('test_strip_non_command.txt', 'assert_strip_non_command.txt'):
            with self.subTest(command=c[0]):
                self.assertEqual(self.commands.strip_non_command(self.prefixes, c[0]), c[1])

    def test_can_raise_notfound(self):
        for i in range(0, 10):
            with self.subTest(channel_id=i):
                self.assertTrue(self.loop.run_until_complete(self.commands.can_raise_notfound(i)))
                self.loop.run_until_complete(self.commands.raise_notfound(i, self.prefixes, "!invalid"))
                self.assertFalse(self.loop.run_until_complete(self.commands.can_raise_notfound(i)))
                self.commands.notfound_timers[i] = datetime.datetime.utcnow() - datetime.timedelta(hours=13)
                self.assertTrue(self.loop.run_until_complete(self.commands.can_raise_notfound(i)))
                self.assertFalse(self.loop.run_until_complete(self.commands.can_raise_notfound(i)))

    def test_raise_notfound(self):
        for i in range(0, 10):
            with self.subTest(channel_id=i):
                with self.assertRaises(InsightExc.userInput.CommandNotFound):
                    self.loop.run_until_complete(self.commands.raise_notfound(i, self.prefixes, "!invalid"))
                self.loop.run_until_complete(self.commands.raise_notfound(i, self.prefixes, "!invalid"))
