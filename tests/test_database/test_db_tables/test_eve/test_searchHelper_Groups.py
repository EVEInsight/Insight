from tests.test_database.test_db_tables.test_eve import test_searchHelper_Characters
from database.db_tables.eve import tb_groups


class TestSearchHelperGroups(test_searchHelper_Characters.TestSearchHelperCharacters):
    @property
    def table(self):
        return tb_groups

    @property
    def name_col(self):
        return tb_groups.name

    @property
    def id_col(self):
        return tb_groups.group_id

    @property
    def insert_id(self):
        return 574

    @property
    def insert_name(self):
        return "Asteroid Serpentis Officer"

    def search_hit_names(self):
        yield "officer"
        yield "astero"

    def search_hit_ids(self):
        yield "57"

    def search_miss_ids(self):
        yield "1574"
        yield "5741"

    def helper_set_name(self, row, name):
        row.name = name
