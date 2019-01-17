from tests.test_database.test_db_tables.test_eve import AbstractTableRowTesting
from database.db_tables.eve import tb_groups, tb_categories, tb_types
from swagger_client import UniverseApi


class TestGroupsBase(AbstractTableRowTesting.AbstractTableRowTesting):
    @property
    def api_not_implemented(self):
        return False

    @property
    def helper_assert_name(self):
        return "Titan"

    @property
    def helper_assert_id(self):
        return 30

    @property
    def helper_row(self):
        return tb_groups

    @property
    def helper_pk(self):
        return tb_groups.group_id

    @property
    def helper_assert_api_category(self):
        return UniverseApi

    def helper_get_name(self, tb_row: tb_groups):
        return tb_row.name

    def helper_set_name_row(self, row: tb_groups, name):
        row.name = name

    def set_foreign_keys(self, row: tb_groups):
        row.category_id = 6
        row._types = [i for i in range(1000, 1250)]

    def helper_assert_foreign_keys(self, row: tb_groups):
        fk_row: tb_categories = row.object_category
        self.assertIsInstance(fk_row, tb_categories)
        self.assertEqual(fk_row.category_id, 6)
        self.assertTrue(row in fk_row.object_groups)
        counter = 0
        for i in row.object_types:
            counter += 1
            self.assertIsInstance(i, tb_types)
            self.assertTrue(i.object_group == row)
        if counter < 250:
            self.fail()
