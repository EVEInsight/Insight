from tests.test_database.test_db_tables.test_eve import test_searchHelper_Characters
from database.db_tables.eve import tb_systems


class TestSearchHelperSystems(test_searchHelper_Characters.TestSearchHelperCharacters):
    @property
    def table(self):
        return tb_systems

    @property
    def name_col(self):
        return tb_systems.name

    @property
    def id_col(self):
        return tb_systems.system_id

    @property
    def insert_id(self):
        return 30004694

    @property
    def insert_name(self):
        return "GQ2S-8"

    def search_hit_names(self):
        yield "GQ2"
        yield "GQ2"
        yield "-8"

    def search_hit_ids(self):
        yield "300046"
