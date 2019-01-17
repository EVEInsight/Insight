from tests.test_database.test_db_tables.test_eve import AbstractNameOnlyTesting
from database.db_tables.eve import tb_systems
from swagger_client import UniverseApi


class TestSystemsNameOnly(AbstractNameOnlyTesting.AbstractNameOnlyTesting):
    @property
    def helper_assert_name(self):
        return "Jita"

    @property
    def helper_assert_id(self):
        return 30000142

    @property
    def helper_row(self):
        return tb_systems

    @property
    def helper_pk(self):
        return tb_systems.system_id

    @property
    def helper_assert_api_category(self):
        return UniverseApi

