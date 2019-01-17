from tests.test_database.test_db_tables.test_eve import AbstractNameOnlyTesting
from database.db_tables.eve import tb_corporations
from swagger_client import UniverseApi


class TestCorporationsNameOnly(AbstractNameOnlyTesting.AbstractNameOnlyTesting):
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
