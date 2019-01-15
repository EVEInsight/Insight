from tests.abstract import DatabaseTesting
from database.db_tables.eve import id_resolver, tb_characters, tb_corporations, tb_alliances
from swagger_client import PostUniverseIdsOk


class TestIdResolve(DatabaseTesting.DatabaseTesting):
    def setUp(self):
        super().setUp()
        self.set_resource_path('db_tables', 'eve', 'mass_id_resolve')

    def test_get_response(self):
        for c in self.iterate_assert_file('lookup_names.txt', 'lookup_ids.txt'):
            with self.subTest(name=c[0]):
                resp = id_resolver.get_response(id_resolver.get_api(id_resolver.get_configuration()), names=[str(c[0])])
                self.assertIsInstance(resp, PostUniverseIdsOk)
                found_result = False
                if isinstance(resp.characters, list):
                    for r in resp.characters:
                        if r.name == c[0]:
                            self.assertEqual(r.id, int(c[1]))
                            found_result = True
                if isinstance(resp.corporations, list):
                    for r in resp.corporations:
                        if r.name == c[0]:
                            self.assertEqual(r.id, int(c[1]))
                            found_result = True
                if isinstance(resp.alliances, list):
                    for r in resp.alliances:
                        if r.name == c[0]:
                            self.assertEqual(r.id, int(c[1]))
                            found_result = True
                if not found_result:
                    self.fail("Not found.")

    def helper_api_mass_id_resolve(self, lookup_names, lookup_ids, run_resolve=False):
        for c in self.iterate_assert_file(lookup_names, lookup_ids):
            lookup_str = str(c[0]).lower()
            with self.subTest(name=c[0], search_str=lookup_str):
                if run_resolve:
                    id_resolver.api_mass_id_resolve(self.service, lookup_str)
                found = False
                for r in self.db.query(tb_characters).all() + self.db.query(tb_corporations).all() + self.db.query(tb_alliances).all():
                    if r.get_id() == int(c[1]):
                        self.assertEqual(r.get_name(), c[0])
                        found = True
                        break
                if not found:
                    self.fail("Not found.")

    def test_api_mass_id_resolve_string(self):
        self.helper_api_mass_id_resolve('lookup_names.txt', 'lookup_ids.txt', True)

    def test_api_mass_id_resolve_list(self):
        lookup_names = [c.lower() for c in self.get_file_lines('lookup_names_long.txt')]
        id_resolver.api_mass_id_resolve(self.service, lookup_names)
        self.helper_api_mass_id_resolve('lookup_names_long.txt', 'lookup_ids_long.txt')
