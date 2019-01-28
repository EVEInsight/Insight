from tests.abstract import InsightTestBase
from InsightUtilities import ColumnEncryption, InsightSingleton
import shutil
import os
import configparser


class TestColumnEncryption(InsightTestBase.InsightTestBase):
    def setUp(self):
        super().setUp()
        self.set_resource_path("config")
        shutil.copy(os.path.join(self.resources, "config.ini"), os.getcwd())
        self.ce = ColumnEncryption()

    def tearDown(self):
        super().tearDown()
        InsightSingleton.clear_instance_references()
        if os.path.exists("config.ini"):
            os.remove("config.ini")

    def helper_current_key_in_file(self):
        cfile = configparser.ConfigParser()
        cfile.read(self.ce._config_file_path)
        return cfile.get("encryption", "secret_key")

    def test__generate_new_key(self):
        k1 = self.ce._generate_new_key()
        self.assertLess(64, len(k1))
        self.assertNotEqual(k1, self.ce._generate_new_key())

    def test__set_key(self):
        k = self.ce._generate_new_key()
        self.ce._set_key(k)
        self.assertEqual(k, self.ce._key)

    def test__load_key(self):
        self.ce._load_key()
        k = self.helper_current_key_in_file()
        self.assertIsInstance(k, str)
        self.assertLess(64, len(k))
        self.assertEqual(k, self.ce._key)
        self.assertEqual(k, self.ce.get_key())
        self.ce._load_key()
        self.assertEqual(k, self.ce._key)

    def test_get_key(self):
        k = self.ce.get_key()
        self.assertIsInstance(k, str)
        self.assertLess(64, len(k))

    def test_reset_key(self):
        k1 = self.ce.get_key()
        self.assertLess(64, len(k1))
        self.assertEqual(k1, self.helper_current_key_in_file())
        self.ce.reset_key()
        k2 = self.ce.get_key()
        self.assertNotEqual(k1, k2)
        self.assertLess(64, len(k2))
        self.assertEqual(k2, self.helper_current_key_in_file())
