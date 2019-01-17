from tests.test_database.test_db_tables.test_eve import AbstractTableRowTesting, AbstractNameOnlyTesting
from database.db_tables.eve import tb_corporations
from swagger_client import UniverseApi
import unittest


class TestCorporationsBase(AbstractTableRowTesting.AbstractTableRowTesting):
    @property
    def api_not_implemented(self):
        return False

    @property
    def helper_assert_name(self):
        return "BURN EDEN"

    @property
    def helper_assert_id(self):
        return 761955047

    @property
    def helper_row(self):
        return tb_corporations

    @property
    def helper_pk(self):
        return tb_corporations.corporation_id

    @property
    def helper_assert_api_category(self):
        return UniverseApi

    def helper_get_name(self, tb_row: tb_corporations):
        return tb_row.corporation_name

    def helper_set_name_row(self, row, name):
        row.corporation_name = name

    @unittest.SkipTest
    def test_load_fk_objects_merge(self):
        super().test_load_fk_objects_merge()

    @unittest.SkipTest
    def test_load_fk_objects_add(self):
        super().test_load_fk_objects_add()
