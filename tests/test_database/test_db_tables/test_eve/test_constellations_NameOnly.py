from tests.test_database.test_db_tables.test_eve import AbstractNameOnlyTesting
from database.db_tables.eve import tb_constellations
from swagger_client import UniverseApi


class TestConstellationsNameOnly(AbstractNameOnlyTesting.AbstractNameOnlyTesting):
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

