from tests.test_database.test_db_tables.test_eve import test_searchHelper_Characters
from database.db_tables.eve import tb_constellations


class TestSearchHelperConstellations(test_searchHelper_Characters.TestSearchHelperCharacters):
    @property
    def table(self):
        return tb_constellations

    @property
    def name_col(self):
        return tb_constellations.name

    @property
    def id_col(self):
        return tb_constellations.constellation_id

    @property
    def insert_id(self):
        return 20000153

    @property
    def insert_name(self):
        return "Heaven"

    def search_hit_names(self):
        yield "Hea"
        yield "he"

    def search_hit_ids(self):
        yield "000015"
