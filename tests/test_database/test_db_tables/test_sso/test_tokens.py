from tests.abstract.TestCases.AbstractSSOTesting import AbstractSSOTesting
from database.db_tables.sso import tb_tokens, tb_contacts_pilots, tb_contacts_corps, tb_contacts_alliances, sso_base
from database.db_tables.eve import tb_characters, tb_corporations, tb_alliances
import unittest
import hashlib
import secrets


class TestTokens(AbstractSSOTesting):
    @classmethod
    def setUpClass(cls):
        cls.token = None

    @classmethod
    def set_token(cls, new_token: str):
        if not isinstance(new_token, str):
            raise ValueError
        cls.token = new_token

    @classmethod
    def get_token(cls):
        return cls.token

    def setUp(self):
        super().setUp()
        self.db.add(tb_tokens(1, self.refresh_token))
        self.db.commit()
        t: tb_tokens = self.helper_get_row(1)
        if self.get_token() is None:
            self.sso.get_token(t)
            self.set_token(t.token)
        t.token = self.get_token()
        self.db.commit()

    @unittest.SkipTest
    def test_str_mod(self):
        self.fail()

    @unittest.SkipTest
    def test_str_upd(self):
        self.fail()

    @unittest.SkipTest
    def test_str_wChcount(self):
        self.fail()

    def test_get_affiliation(self):
        t: tb_tokens = self.helper_get_row(1)
        t.get_affiliation(t.token, self.service)
        self.assertIsInstance(t.object_pilot, tb_characters)
        self.assertIsInstance(t.object_corp, tb_corporations)
        self.assertIsInstance(t.object_alliance, tb_alliances)
        self.service.get_session().commit()
        t: tb_tokens = self.helper_get_row(1)
        self.assertEqual(self.assert_char_id, t.character_id)
        self.assertEqual(self.assert_corp_id, t.corporation_id)
        self.assertEqual(self.assert_alliance_id, t.alliance_id)

    @unittest.SkipTest
    def test_get_results(self):
        self.fail()

    @unittest.SkipTest
    def test_process_contact(self):
        self.fail()

    @unittest.SkipTest
    def test_write_changes(self):
        self.fail()

    def test_update_contacts(self):
        t = self.helper_get_row(1)
        t.character_id = self.assert_char_id
        t.corporation_id = self.assert_corp_id
        t.alliance_id = self.assert_alliance_id
        t.update_contacts(self.service)
        self.db.commit()
        t = self.helper_get_row(1)
        self.assertIsInstance(t.etag_character, str)
        self.assertIsInstance(t.etag_corp, str)
        self.assertIsInstance(t.etag_alliance, str)
        self.assertLess(200, len(t.object_contacts_pilots))
        self.assertLess(50, len(t.object_contacts_corps))
        self.assertLess(50, len(t.object_contacts_alliances))
        self.db.query(tb_contacts_pilots).filter(tb_contacts_pilots.token == t.token_id,
                                                 tb_contacts_pilots.character_id == self.assert_char_id,
                                                 tb_contacts_pilots.standing == 10.0).one()
        self.db.query(tb_contacts_corps).filter(tb_contacts_corps.token == t.token_id,
                                                tb_contacts_corps.corporation_id == self.assert_corp_id,
                                                tb_contacts_corps.standing == 10.0).one()
        self.db.query(tb_contacts_alliances).filter(tb_contacts_alliances.token == t.token_id,
                                                    tb_contacts_alliances.alliance_id == self.assert_alliance_id,
                                                    tb_contacts_alliances.standing == 10.0).one()
        owner_enums = [t.owner for t in t.object_contacts_pilots + t.object_contacts_corps + t.object_contacts_alliances]
        self.assertTrue(sso_base.contact_owner.pilot in owner_enums)
        self.assertTrue(sso_base.contact_owner.corp in owner_enums)
        self.assertTrue(sso_base.contact_owner.alliance in owner_enums)

    @unittest.SkipTest  # unable to provide auth codes in unit tests due to 15 minute time constraint
    def test_generate_from_auth(self):
        self.fail()

    def test_sync_all_tokens(self):
        t1 = self.helper_get_row(1).token
        tb_tokens.sync_all_tokens(1, self.service)
        t2 = self.helper_get_row(1)
        key = secrets.token_urlsafe(64)
        t1_hash = hashlib.sha256((key + ':' + t1).encode('utf-8')).hexdigest()
        t2_hash = hashlib.sha256((key + ':' + t2.token).encode('utf-8')).hexdigest()
        self.assertNotEqual(t1_hash, t2_hash)
        self.assertIsInstance(t2.token, str)
        self.set_token(t2.token)

    @unittest.SkipTest
    def test_mass_sync_all(self):
        self.fail()

    def test_delete_noTracking(self):
        t: tb_tokens = self.helper_get_row(1)
        t.character_id = self.assert_char_id
        self.db.commit()
        tb_tokens.delete_noTracking(self.service)
        self.assertIsInstance(self.db.query(tb_tokens).filter(tb_tokens.discord_user == 1).one_or_none(), tb_tokens)
