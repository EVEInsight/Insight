from tests.test_database.test_db_tables.test_eve import AbstractTableRowTesting
from database.db_tables.eve import tb_types, tb_groups
from swagger_client import UniverseApi


class TestTypesBase(AbstractTableRowTesting.AbstractTableRowTesting):
    @property
    def api_not_implemented(self):
        return False

    @property
    def helper_assert_name(self):
        return "Scorch L"

    @property
    def helper_assert_id(self):
        return 12820

    @property
    def helper_row(self):
        return tb_types

    @property
    def helper_pk(self):
        return tb_types.type_id

    @property
    def helper_assert_api_category(self):
        return UniverseApi

    def helper_get_name(self, tb_row: tb_types):
        return tb_row.type_name

    def helper_set_name_row(self, row: tb_types, name):
        row.type_name = name

    def set_foreign_keys(self, row: tb_types):
        row.group_id = 30

    def helper_assert_foreign_keys(self, row: tb_types):
        fk_row = row.object_group
        self.assertIsInstance(fk_row, tb_groups)
        self.assertEqual(fk_row.group_id, 30)
        self.assertTrue(row in fk_row.object_types)
