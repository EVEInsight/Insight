from tests.test_database.test_db_tables.test_eve import AbstractTableRowTesting
from database.db_tables.eve import tb_constellations, tb_regions, tb_systems
from swagger_client import UniverseApi


class TestConstellationsBase(AbstractTableRowTesting.AbstractTableRowTesting):
    @property
    def api_not_implemented(self):
        return False

    @property
    def helper_assert_name(self):
        return "Heaven"

    @property
    def helper_assert_id(self):
        return 20000153

    @property
    def helper_row(self):
        return tb_constellations

    @property
    def helper_pk(self):
        return tb_constellations.constellation_id

    @property
    def helper_assert_api_category(self):
        return UniverseApi

    def helper_get_name(self, tb_row: tb_constellations):
        return tb_row.name

    def helper_set_name_row(self, row: tb_constellations, name):
        row.name = name

    def set_foreign_keys(self, row: tb_constellations):
        row.region_id = 20000153
        row._systems = [i for i in range(1000, 1250)]

    def helper_assert_foreign_keys(self, row: tb_constellations):
        region_row: tb_regions = row.object_region
        self.assertIsInstance(region_row, tb_regions)
        self.assertEqual(region_row.region_id, 20000153)
        self.assertTrue(row in region_row.object_constellations)
        counter = 0
        for i in row.object_systems:
            counter += 1
            self.assertIsInstance(i, tb_systems)
            self.assertTrue(i.object_constellation == row)
        if counter < 250:
            self.fail()
