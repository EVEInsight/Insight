from tests.test_database.test_db_tables.test_eve import AbstractTableRowTesting
from database.db_tables.eve import tb_regions, tb_constellations
from swagger_client import UniverseApi


class TestRegionsBase(AbstractTableRowTesting.AbstractTableRowTesting):
    @property
    def api_not_implemented(self):
        return False

    @property
    def helper_assert_name(self):
        return "Delve"

    @property
    def helper_assert_id(self):
        return 10000060

    @property
    def helper_row(self):
        return tb_regions

    @property
    def helper_pk(self):
        return tb_regions.region_id

    @property
    def helper_assert_api_category(self):
        return UniverseApi

    def helper_get_name(self, tb_row: tb_regions):
        return tb_row.name

    def helper_set_name_row(self, row: tb_regions, name):
        row.name = name

    def set_foreign_keys(self, row: tb_regions):
        row._constellations = [i for i in range(1000, 1250)]

    def helper_assert_foreign_keys(self, row: tb_regions):
        counter = 0
        for i in row.object_constellations:
            counter += 1
            self.assertIsInstance(i, tb_constellations)
            self.assertTrue(i.object_region == row)
        if counter < 250:
            self.fail()
