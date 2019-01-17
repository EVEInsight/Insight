from tests.test_database.test_db_tables.test_eve import test_searchHelper_Characters
from database.db_tables.eve import tb_types


class TestSearchHelperTypes(test_searchHelper_Characters.TestSearchHelperCharacters):
    @property
    def table(self):
        return tb_types

    @property
    def name_col(self):
        return tb_types.type_name

    @property
    def id_col(self):
        return tb_types.type_id

    @property
    def insert_id(self):
        return 24698

    @property
    def insert_name(self):
        return "Drake"

    def search_hit_names(self):
        yield "ra"
        yield "ke"

    def search_hit_ids(self):
        yield "246"

    def search_miss_ids(self):
        yield "124698"
        yield "124698"
