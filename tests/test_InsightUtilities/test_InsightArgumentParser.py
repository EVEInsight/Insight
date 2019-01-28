from tests.abstract import InsightTestBase
from InsightUtilities import InsightArgumentParser
from argparse import Namespace


class TestInsightArgumentParser(InsightTestBase.InsightTestBase):
    def setUp(self):
        super().setUp()
        self.a = InsightArgumentParser.get_cli_args()

    def test_get_cli_args(self):
        self.assertIsInstance(self.a, Namespace)

    def test_config(self):
        self.assertEqual("config.ini", self.a.config)


class TestInsightArgumentParserHelp(InsightTestBase.InsightTestBase):
    def setUp(self):
        super().setUp()
        self.set_sys_args("--help", "testing", "--ws")

    def test_get_cli_args(self):
        with self.assertRaises(SystemExit) as ex:
            InsightArgumentParser.get_cli_args()
        self.assertEqual(0, ex.exception.code)
