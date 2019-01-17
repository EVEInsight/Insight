from tests.test_database.test_db_tables.test_eve import AbstractTableRowTesting
from database.db_tables.eve import tb_categories, tb_groups
from swagger_client import UniverseApi


class TestCategoryBase(AbstractTableRowTesting.AbstractTableRowTesting):
    @property
    def api_not_implemented(self):
        return False

    @property
    def helper_assert_name(self):
        return "Ship"

    @property
    def helper_assert_id(self):
        return 6

    @property
    def helper_row(self):
        return tb_categories

    @property
    def helper_pk(self):
        return tb_categories.category_id

    @property
    def helper_assert_api_category(self):
        return UniverseApi

    def helper_get_name(self, tb_row: tb_categories):
        return tb_row.name

    def helper_set_name_row(self, row, name):
        row.name = name

    def set_foreign_keys(self, row: tb_categories):
        row._groups = [i for i in range(1000, 1250)]

    def helper_assert_foreign_keys(self, row: tb_categories):
        counter = 0
        for i in row.object_groups:
            counter += 1
            self.assertIsInstance(i, tb_groups)
            self.assertTrue(i.object_category == row)
        if counter < 250:
            self.fail()
