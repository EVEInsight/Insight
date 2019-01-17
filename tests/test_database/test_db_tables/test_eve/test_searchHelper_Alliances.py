from tests.test_database.test_db_tables.test_eve import test_searchHelper_Characters
from database.db_tables.eve import tb_alliances


class TestSearchHelperAlliances(test_searchHelper_Characters.TestSearchHelperCharacters):
    @property
    def table(self):
        return tb_alliances

    @property
    def name_col(self):
        return tb_alliances.alliance_name

    @property
    def id_col(self):
        return tb_alliances.alliance_id

    @property
    def insert_id(self):
        return 1727758877

    @property
    def insert_name(self):
        return "Northern Coalition."

    def search_hit_names(self):
        yield "north"
        yield "coalition"
        yield "rthern Co"

    def search_hit_ids(self):
        yield "1727758877"
        yield "277588"
