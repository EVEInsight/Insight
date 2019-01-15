from tests.abstract import DatabaseTesting
from database.db_tables.eve import name_resolver, tb_characters, tb_corporations, tb_alliances
import requests


class TestMassNameResolve(DatabaseTesting.DatabaseTesting):
    def setUp(self):
        super().setUp()
        self.set_resource_path('db_tables', 'eve', 'mass_name_resolve')
        self.f_id_chars = self.get_file_lines('id_characters.txt')
        self.f_id_corps = self.get_file_lines('id_corps.txt')
        self.f_id_alliances = self.get_file_lines('id_alliances.txt')
        for i in self.f_id_chars:
            self.db.add(tb_characters(int(i)))
        for i in self.f_id_corps:
            self.db.add(tb_corporations(int(i)))
        for i in self.f_id_alliances:
            self.db.add(tb_alliances(int(i)))
        self.db.commit()

    def helper_len_ids(self):
        return len(self.f_id_chars) + len(self.f_id_corps) + len(self.f_id_alliances)

    def test_post_url(self):
        url = name_resolver.post_url()
        self.assertEqual(url, "https://esi.evetech.net/latest/universe/names/?datasource=tranquility")
        self.assertEqual(requests.post(url, json=[1326083433]).status_code, 200)  # check if url still works

    def test_missing_count(self):
        self.assertEqual(name_resolver.missing_count(self.service), self.helper_len_ids())

    def test_api_mass_name_resolve_valid(self):
        self.assertEqual(len(name_resolver.api_mass_name_resolve(self.service)), 0)
        for i in self.iterate_assert_file(self.f_id_chars, 'name_characters.txt'):
            with self.subTest(char_id=i[0]):
                self.assertEqual(tb_characters.get_row(int(i[0]), self.service).get_name(), i[1])
        for i in self.iterate_assert_file(self.f_id_corps, 'name_corps.txt'):
            with self.subTest(corp_id=i[0]):
                self.assertEqual(tb_corporations.get_row(int(i[0]), self.service).get_name(), i[1])
        for i in self.iterate_assert_file(self.f_id_alliances, 'name_alliances.txt'):
            with self.subTest(alliance_id=i[0]):
                self.assertEqual(tb_alliances.get_row(int(i[0]), self.service).get_name(), i[1])

    def test_api_mass_name_resolve_invalid(self):
        self.assertEqual(len(name_resolver.api_mass_name_resolve(self.service)), 0)
        self.db.add(tb_characters(55))
        self.db.commit()
        self.assertNotEqual(len(name_resolver.api_mass_name_resolve(self.service)), 0)
