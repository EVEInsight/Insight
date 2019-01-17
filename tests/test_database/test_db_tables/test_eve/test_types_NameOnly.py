from tests.test_database.test_db_tables.test_eve import AbstractNameOnlyTesting
from database.db_tables.eve import tb_types
from swagger_client import UniverseApi


class TestTypesNameOnly(AbstractNameOnlyTesting.AbstractNameOnlyTesting):
    @property
    def helper_assert_name(self):
        return "Scorch L"

    @property
    def helper_assert_id(self):
        return 12820

    @property
    def helper_row(self):
        return tb_types

    @property
    def helper_pk(self):
        return tb_types.type_id

    @property
    def helper_assert_api_category(self):
        return UniverseApi

