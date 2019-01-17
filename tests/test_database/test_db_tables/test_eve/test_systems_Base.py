from tests.test_database.test_db_tables.test_eve import AbstractTableRowTesting
from database.db_tables.eve import tb_systems, tb_constellations
from swagger_client import UniverseApi


class TestSystemsBase(AbstractTableRowTesting.AbstractTableRowTesting):
    @property
    def api_not_implemented(self):
        return False

    @property
    def helper_assert_name(self):
        return "Jita"

    @property
    def helper_assert_id(self):
        return 30000142

    @property
    def helper_row(self):
        return tb_systems

    @property
    def helper_pk(self):
        return tb_systems.system_id

    @property
    def helper_assert_api_category(self):
        return UniverseApi

    def helper_get_name(self, tb_row: tb_systems):
        return tb_row.name

    def helper_set_name_row(self, row: tb_systems, name):
        row.name = name

    def set_foreign_keys(self, row: tb_systems):
        row.constellation_id = 20000153

    def helper_assert_foreign_keys(self, row: tb_systems):
        const_row = row.object_constellation
        self.assertIsInstance(const_row, tb_constellations)
        self.assertEqual(const_row.constellation_id, 20000153)
        self.assertTrue(row in const_row.object_systems)

