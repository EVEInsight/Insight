from tests.test_database.test_db_tables.test_eve import test_mass_name_resolve
from database.db_tables.eve import name_resolver, tb_characters, tb_corporations, tb_alliances
import unittest


class TestMassNameResolve2(test_mass_name_resolve.TestMassNameResolve):
    def setUp(self):
        super(test_mass_name_resolve.TestMassNameResolve, self).setUp()
        self.set_resource_path('db_tables', 'eve', 'mass_name_resolve')
        self.f_id_chars = self.get_file_lines('id_characters_large.txt')
        self.f_id_corps = self.get_file_lines('id_corps_large.txt')
        self.f_id_alliances = self.get_file_lines('id_alliances_large.txt')
        for i in self.f_id_chars:
            self.db.add(tb_characters(int(i)))
        for i in self.f_id_corps:
            self.db.add(tb_corporations(int(i)))
        for i in self.f_id_alliances:
            self.db.add(tb_alliances(int(i)))
        self.db.commit()

    def test_api_mass_name_resolve_valid(self):
        self.assertEqual(len(name_resolver.api_mass_name_resolve(self.service)), 0)
        for i in self.db.query(tb_characters).all():
            self.assertIsInstance(i.get_name(), str)
        for i in self.db.query(tb_corporations).all():
            self.assertIsInstance(i.get_name(), str)
        for i in self.db.query(tb_alliances).all():
            self.assertIsInstance(i.get_name(), str)

    @unittest.SkipTest
    def test_post_url(self):
        return

    @unittest.SkipTest
    def test_api_mass_name_resolve_invalid(self):
        return
