from tests.test_database.test_db_tables.test_eve import AbstractTableRowTesting
from database.db_tables.eve import tb_alliances
from swagger_client import UniverseApi
import unittest


class TestAlliancesBase(AbstractTableRowTesting.AbstractTableRowTesting):
    @property
    def api_not_implemented(self):
        return False

    @property
    def helper_assert_name(self):
        return "Northern Coalition."

    @property
    def helper_assert_id(self):
        return 1727758877

    @property
    def helper_row(self):
        return tb_alliances

    @property
    def helper_pk(self):
        return tb_alliances.alliance_id

    @property
    def helper_assert_api_category(self):
        return UniverseApi

    def helper_get_name(self, tb_row: tb_alliances):
        return tb_row.alliance_name

    def helper_set_name_row(self, row, name):
        row.alliance_name = name

    @unittest.SkipTest
    def test_load_fk_objects_merge(self):
        super().test_load_fk_objects_merge()

    @unittest.SkipTest
    def test_load_fk_objects_add(self):
        super().test_load_fk_objects_add()
