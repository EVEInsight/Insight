from tests.test_database.test_db_tables.test_eve import AbstractTableRowTesting
from database.db_tables.eve import tb_locations
from swagger_client import UniverseApi
import unittest


class TestLocationsBase(AbstractTableRowTesting.AbstractTableRowTesting):
    @property
    def api_not_implemented(self):
        return True

    @property
    def helper_assert_name(self):
        return "Taisy V - Asteroid Belt 1"

    @property
    def helper_assert_id(self):
        return 40092171

    @property
    def helper_row(self):
        return tb_locations

    @property
    def helper_pk(self):
        return tb_locations.location_id

    @property
    def helper_assert_api_category(self):
        return UniverseApi

    def helper_get_name(self, tb_row: tb_locations):
        return tb_row.name

    def helper_set_name_row(self, row: tb_locations, name):
        row.name = name

    @unittest.SkipTest
    def test_load_fk_objects_merge(self):
        super().test_load_fk_objects_merge()

    @unittest.SkipTest
    def test_load_fk_objects_add(self):
        super().test_load_fk_objects_add()
