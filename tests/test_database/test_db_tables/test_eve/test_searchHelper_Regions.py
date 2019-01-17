from tests.test_database.test_db_tables.test_eve import test_searchHelper_Characters
from database.db_tables.eve import tb_regions


class TestSearchHelperRegions(test_searchHelper_Characters.TestSearchHelperCharacters):
    @property
    def table(self):
        return tb_regions

    @property
    def name_col(self):
        return tb_regions.name

    @property
    def id_col(self):
        return tb_regions.region_id

    @property
    def insert_id(self):
        return 10000012

    @property
    def insert_name(self):
        return "Curse"

    def search_hit_names(self):
        yield "cu"
        yield "rse"

    def search_hit_ids(self):
        yield "100000"

    def search_miss_ids(self):
        yield "10000013"
        yield "100000123"
