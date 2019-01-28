from tests.abstract import DatabaseTesting
from service import EVEsso
import os
from InsightUtilities import InsightSingleton, ColumnEncryption
from database.db_tables.sso import tb_tokens
import unittest


def sso_variables():
    yield from ["sso_client_id", "sso_secret_key", "sso_callback_url", "sso_refresh_token", "sso_char_id",
                "sso_corp_id", "sso_alliance_id"]


def missing_sso_environmental():
    for v in sso_variables():
        if os.environ.get(v) is None:
            return True
    return False


def missing_sso_message():
    return "Missing SSO environmental variables for testing the SSO system. This test class has been skipped. " \
           "You must set the following environmental variables:\n{}".format('\n'.join(sso_variables()))


@unittest.skipIf(missing_sso_environmental(), missing_sso_message())
class AbstractSSOTesting(DatabaseTesting.DatabaseTesting):
    def setUp(self):
        super().setUp()
        ColumnEncryption()._set_random_key()
        self.sso = EVEsso.EVEsso(self.service)
        self.service.sso = self.sso
        self.client_id = os.environ.get("sso_client_id")
        self.secret_key = os.environ.get("sso_secret_key")
        self.callback_url = os.environ.get("sso_callback_url")
        self.refresh_token = os.environ.get("sso_refresh_token")
        self.assert_char_id = int(os.environ.get("sso_char_id"))
        self.assert_corp_id = int(os.environ.get("sso_corp_id"))
        self.assert_alliance_id = int(os.environ.get("sso_alliance_id"))
        self.assert_sso_login = "https://login.eveonline.com/oauth/authorize?response_type=code&redirect_uri={}" \
                                "&client_id={}&scope=esi-characters.read_contacts.v1%20esi-corporations.read_" \
                                "contacts.v1%20esi-alliances.read_contacts.v1".format(self.callback_url, self.client_id)

    def tearDown(self):
        super().tearDown()
        InsightSingleton.clear_instance_references()

    def helper_get_row(self, discord_user)->tb_tokens:
        return self.service.get_session().query(tb_tokens).filter(tb_tokens.discord_user == discord_user).one() # can have multiple by filter but assume one for this test case
