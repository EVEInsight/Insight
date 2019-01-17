from tests.test_database.test_db_tables.test_eve import AbstractNameOnlyTesting
from database.db_tables.eve import tb_alliances
from swagger_client import UniverseApi


class TestAlliancesNameOnly(AbstractNameOnlyTesting.AbstractNameOnlyTesting):
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
