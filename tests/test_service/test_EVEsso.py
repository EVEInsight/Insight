from tests.abstract import DatabaseTesting
from service import EVEsso
from tests.mocks import ServiceModule
import unittest
import os
from database.db_tables.sso import tb_tokens


def missing_sso_environmental():
    return os.environ.get("sso_client_id") is None or os.environ.get("sso_secret_key") is None \
           or os.environ.get("sso_callback_url") is None


def missing_sso_message():
    return "Missing SSO environmental variables for testing the SSO system. This test has been skipped."


class TestEVEsso(DatabaseTesting.DatabaseTesting):
    def setUp(self):
        super().setUp()
        self.sso = EVEsso.EVEsso(self.service)
        self.client_id = os.environ.get("sso_client_id")
        self.secret_key = os.environ.get("sso_secret_key")
        self.callback_url = os.environ.get("sso_callback_url")
        self.assert_sso_login = "https://login.eveonline.com/oauth/authorize?response_type=code&redirect_uri={}" \
                                "&client_id={}&scope=esi-characters.read_contacts.v1%20esi-corporations.read_" \
                                "contacts.v1%20esi-alliances.read_contacts.v1".format(self.callback_url, self.client_id)
        # self.db.add(tb_tokens(1, 12345))
        # self.db.commit()

    @unittest.skipIf(missing_sso_environmental(), missing_sso_message())
    def test__get_config(self):  # implied call by init in setUp
        self.assertEqual(self.sso._client_id, self.client_id)
        self.assertIsInstance(self.sso._client_secret, str)
        self.assertEqual(self.assert_sso_login, self.sso._login_url)

    @unittest.skipIf(missing_sso_environmental(), missing_sso_message())
    def test__get_scopes(self):
        self.assertEqual("esi-characters.read_contacts.v1%20esi-corporations.read_contacts.v1%20esi-alliances."
                         "read_contacts.v1", self.sso._get_scopes())

    @unittest.skipIf(missing_sso_environmental(), missing_sso_message())
    def test_get_callback_example(self):
        self.assertEqual(self.callback_url + "?code=ExampleCallbackAuthCode", self.sso.get_callback_example())

    @unittest.skipIf(missing_sso_environmental(), missing_sso_message())
    def test_get_sso_login(self):
        self.assertEqual(self.assert_sso_login, self.sso.get_sso_login())

    @unittest.skipIf(missing_sso_environmental(), missing_sso_message())
    def test_clean_auth_code(self):
        self.assertEqual("ExampleCallbackAuthCode",
                         self.sso.clean_auth_code("https://nathan-s.com/?code=ExampleCallbackAuthCode"))
        self.assertEqual("ExampleCallbackAuthCode",
                         self.sso.clean_auth_code("https://nathan-s.com?code=ExampleCallbackAuthCode"))
        with self.assertRaises(KeyError):
            self.sso.clean_auth_code("https://nathan-s.com=ExampleCallbackAuthCode")

    @unittest.SkipTest
    @unittest.skipIf(missing_sso_environmental(), missing_sso_message())
    def test_get_token_from_auth(self):
        self.fail()

    @unittest.SkipTest
    @unittest.skipIf(missing_sso_environmental(), missing_sso_message())
    def test_get_token(self):
        self.fail()

    @unittest.SkipTest
    @unittest.skipIf(missing_sso_environmental(), missing_sso_message())
    def test_delete_token(self):
        self.fail()

    @unittest.SkipTest
    @unittest.skipIf(missing_sso_environmental(), missing_sso_message())
    def test_get_char(self):
        self.fail()
