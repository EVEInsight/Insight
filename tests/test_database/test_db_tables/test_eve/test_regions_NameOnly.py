from tests.test_database.test_db_tables.test_eve import AbstractNameOnlyTesting
from database.db_tables.eve import tb_regions
from swagger_client import UniverseApi


class TestRegionsNameOnly(AbstractNameOnlyTesting.AbstractNameOnlyTesting):
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

