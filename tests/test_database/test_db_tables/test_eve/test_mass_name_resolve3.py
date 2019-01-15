from tests.test_database.test_db_tables.test_eve import test_mass_name_resolve
from database.db_tables.eve import name_resolver, tb_systems, tb_constellations, tb_regions, tb_types
import unittest


class TestMassNameResolve3(test_mass_name_resolve.TestMassNameResolve):
    def setUp(self):
        super(test_mass_name_resolve.TestMassNameResolve, self).setUp()
        self.set_resource_path('db_tables', 'eve', 'mass_name_resolve')
        self.f_id_systems = self.get_file_lines('id_systems.txt')
        self.f_id_constellations = self.get_file_lines('id_constellations.txt')
        self.f_id_regions = self.get_file_lines('id_regions.txt')
        self.f_id_types = self.get_file_lines('id_types.txt')
        for i in self.f_id_systems:
            self.db.add(tb_systems(int(i)))
        for i in self.f_id_constellations:
            self.db.add(tb_constellations(int(i)))
        for i in self.f_id_regions:
            self.db.add(tb_regions(int(i)))
        for i in self.f_id_types:
            self.db.add(tb_types(int(i)))
        self.db.commit()

    def helper_len_ids(self):
        return len(self.f_id_systems) + len(self.f_id_constellations) + len(self.f_id_regions) + len(self.f_id_types)

    def test_api_mass_name_resolve_valid(self):
        self.assertEqual(len(name_resolver.api_mass_name_resolve(self.service)), 0)
        for i in self.iterate_assert_file(self.f_id_systems, 'name_systems.txt'):
            with self.subTest(system_id=i[0]):
                self.assertEqual(tb_systems.get_row(int(i[0]), self.service).get_name(), i[1])
        for i in self.iterate_assert_file(self.f_id_constellations, 'name_constellations.txt'):
            with self.subTest(constellation_id=i[0]):
                self.assertEqual(tb_constellations.get_row(int(i[0]), self.service).get_name(), i[1])
        for i in self.iterate_assert_file(self.f_id_regions, 'name_regions.txt'):
            with self.subTest(region_id=i[0]):
                self.assertEqual(tb_regions.get_row(int(i[0]), self.service).get_name(), i[1])
        for i in self.iterate_assert_file(self.f_id_types, 'name_types.txt'):
            with self.subTest(type_id=i[0]):
                self.assertEqual(tb_types.get_row(int(i[0]), self.service).get_name(), i[1])

    @unittest.SkipTest
    def test_post_url(self):
        return

    @unittest.SkipTest
    def test_api_mass_name_resolve_invalid(self):
        return
