from tests.abstract.InsightTestBase import InsightTestBase
from tests.mocks.ServiceModule import ServiceModule, ServiceModuleMock2
from unittest.mock import MagicMock
from distutils.version import LooseVersion
import unittest


class TestServiceModuleUpdatingOld(InsightTestBase):
    def setUp(self):
        super().setUp()
        self.service = ServiceModule(None)
        self.service.get_version = MagicMock(return_value=LooseVersion("v0.1"))

    @unittest.SkipTest  # there is something wrong with this test on travis. Travis banned from GitHub api maybe?
    def test_update_available(self):
        self.assertTrue(self.service.update_available())


class TestServiceModuleUpdatingNew(InsightTestBase):
    def setUp(self):
        super().setUp()
        self.service = ServiceModule(None)
        self.service.get_version = MagicMock(return_value=LooseVersion("v10"))

    @unittest.SkipTest
    def test_update_available(self):
        self.assertFalse(self.service.update_available())


class TestServiceModuleNoMockWithConfigFile(InsightTestBase):
    def setUp(self):
        super().setUp()
        self.config_path = self.get_resource_path("config")
        self.copy_file_into_cwid(self.config_path, "config.ini")
        self.set_sys_args("-noapi")
        self.service = ServiceModuleMock2()

    def tearDown(self):
        super().tearDown()
        self.remove_file("motd.txt")
        self.remove_file("config.ini")

    def test_get_headers(self):
        self.assertEqual({}, self.service._header_dict)
        with self.subTest("aiohttp"):
            h = self.service.get_headers()
            self.assertEqual(h, self.service._header_dict.get("aiohttp"))
            self.assertEqual(h.get("Maintainer"), "admin@eveinsight.net (https://github.eveinsight.net)")
            self.assertTrue("aiohttp/" in h.get("User-Agent"))
        with self.subTest("requests"):
            h = self.service.get_headers(lib_requests=True)
            self.assertEqual(h, self.service._header_dict.get("requests"))
            self.assertEqual(h.get("Maintainer"), "admin@eveinsight.net (https://github.eveinsight.net)")
            self.assertTrue("requests/" in h.get("User-Agent"))

    def test_get_config_file(self):
        with self.subTest("Existing config file"):
            self.service.get_config_file("config.ini")
        with self.subTest("Config file does not exist and exits program"):
            with self.assertRaises(SystemExit) as ex:
                self.service.get_config_file("config2.ini")
            self.assertEqual(1, ex.exception.code)

    def test_read_motd(self):
        self.assertEqual(None, self.service._read_motd())  # empty motd file created
        self.assertEqual(None, self.service._read_motd())  # read from empty motd
        self.append_file("motd.txt", "This is a demo MOTD.")  # read from edited motd
        self.assertEqual("This is a demo MOTD.", self.service._read_motd())

    def test_welcome(self):
        self.service.welcome()  # just make sure there are no exceptions raised when calling this function

    def test_get_version(self):
        self.assertIsInstance(self.service.get_version(), LooseVersion)

    def test_get_db_version(self):
        self.assertIsInstance(self.service.get_db_version(), LooseVersion)
