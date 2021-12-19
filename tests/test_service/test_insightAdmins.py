from tests.abstract import InsightTestBase
from service import InsightAdmins
import os
from tests.mocks.ConfigLoader import ConfigLoader


class TestInsightAdminsNone(InsightTestBase.InsightTestBase):
    def setUp(self):
        super().setUp()
        self.config: ConfigLoader = ConfigLoader()
        self.config.config_mapping["INSIGHT_ADMINS"] = []
        self.admins = InsightAdmins.InsightAdmins()

    def tearDown(self):
        super().tearDown()
        if os.path.exists("InsightAdmins.txt"):
            os.remove("InsightAdmins.txt")

    def test__read_admins(self):
        self.assertEqual(0, len(self.admins._admins))

    def test_is_admin(self):
        for i in range(0, 1000):
            self.assertFalse(self.admins.is_admin(self.random_int(10000, 100000000)))

    def test_get_default_admin(self):
        self.assertEqual(None, self.admins.get_default_admin())


class TestInsightAdminsMulti(TestInsightAdminsNone):
    def setUp(self):
        super().setUp()
        self.config.config_mapping["INSIGHT_ADMINS"] = [100000000000000, 100000000000001]
        self.admins = InsightAdmins.InsightAdmins()

    def test__read_admins(self):
        self.assertEqual(2, len(self.admins._admins))

    def test_is_admin(self):
        for i in range(0, 1000):
            self.assertFalse(self.admins.is_admin(self.random_int(10000, 100000000)))
        self.assertTrue(self.admins.is_admin(100000000000000))
        self.assertTrue(self.admins.is_admin(100000000000001))
        self.assertFalse(self.admins.is_admin(100000000000002))

    def test_get_default_admin(self):
        self.assertEqual(100000000000000, self.admins.get_default_admin())
