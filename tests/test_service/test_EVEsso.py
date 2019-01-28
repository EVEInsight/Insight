from tests.abstract.TestCases.AbstractSSOTesting import AbstractSSOTesting
import unittest
from database.db_tables.sso import tb_tokens


class TestEVEsso(AbstractSSOTesting):
    def setUp(self):
        super().setUp()
        self.db.add(tb_tokens(1, self.refresh_token))
        self.db.commit()

    @unittest.SkipTest
    def test__console_auth_mode(self):
        self.fail()

    def test__get_config(self):  # implied call by init in setUp
        self.assertEqual(self.sso._client_id, self.client_id)
        self.assertIsInstance(self.sso._client_secret, str)
        self.assertEqual(self.assert_sso_login, self.sso._login_url)

    def test__get_scopes(self):
        self.assertEqual("esi-characters.read_contacts.v1%20esi-corporations.read_contacts.v1%20esi-alliances."
                         "read_contacts.v1", self.sso._get_scopes())

    def test_get_callback_example(self):
        self.assertEqual(self.callback_url + "?code=ExampleCallbackAuthCode", self.sso.get_callback_example())

    def test_get_sso_login(self):
        self.assertEqual(self.assert_sso_login, self.sso.get_sso_login())

    def test_clean_auth_code(self):
        self.assertEqual("ExampleCallbackAuthCode",
                         self.sso.clean_auth_code("https://nathan-s.com/?code=ExampleCallbackAuthCode"))
        self.assertEqual("ExampleCallbackAuthCode",
                         self.sso.clean_auth_code("https://nathan-s.com?code=ExampleCallbackAuthCode"))
        with self.assertRaises(KeyError):
            self.sso.clean_auth_code("https://nathan-s.com=ExampleCallbackAuthCode")

    @unittest.SkipTest
    def test_get_token_from_auth(self):
        self.fail()

    def test_get_token(self):
        self.assertEqual(None, self.helper_get_row(1).token)
        t: tb_tokens = self.helper_get_row(1)
        self.sso.get_token(t)
        self.assertLess(64, len(t.token))
        self.assertIsInstance(t.token, str)
        self.assertEqual(0, t.error_count)

    @unittest.SkipTest
    def test_delete_token(self):
        self.fail()

    def test_get_char(self):
        t: tb_tokens = self.helper_get_row(1)
        self.sso.get_token(t)
        self.assertEqual(self.assert_char_id, int(self.sso.get_char(t.token)))
