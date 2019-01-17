from tests.test_database.test_db_tables.test_eve import test_searchHelper_Characters
from database.db_tables.eve import tb_corporations


class TestSearchHelperCorporations(test_searchHelper_Characters.TestSearchHelperCharacters):
    @property
    def table(self):
        return tb_corporations

    @property
    def name_col(self):
        return tb_corporations.corporation_name

    @property
    def id_col(self):
        return tb_corporations.corporation_id

    @property
    def insert_id(self):
        return 761955047

    @property
    def insert_name(self):
        return "BURN EDEN"

    def search_hit_names(self):
        yield "Burn"
        yield "Eden"
        yield "urn ed"

    def search_miss_names(self):
        yield "nurb nede"
        yield "Ai"

    def search_hit_ids(self):
        yield "761955047"
        yield "95504"


class TestSearchHelperCorporations2(TestSearchHelperCorporations):
    @property
    def insert_id(self):
        return 1673385956

    @property
    def insert_name(self):
        return "Syndicate Enterprise"

    def search_hit_names(self):
        yield "Synd"
        yield "enter"
        yield "syn"

    def search_hit_ids(self):
        yield "1673385956"
