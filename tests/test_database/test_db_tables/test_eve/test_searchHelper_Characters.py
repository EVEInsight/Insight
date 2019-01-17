from tests.abstract import DatabaseTesting
from database.db_tables.eve import tb_characters, SearchHelper


class TestSearchHelperCharacters(DatabaseTesting.DatabaseTesting):
    @property
    def table(self):
        return tb_characters

    @property
    def name_col(self):
        return tb_characters.character_name

    @property
    def id_col(self):
        return tb_characters.character_id

    @property
    def insert_id(self):
        return 1326083433

    @property
    def insert_name(self):
        return "Natuli"

    def search_hit_names(self):
        yield "Nat"
        yield "atu"

    def search_miss_names(self):
        yield "Ta"
        yield "Ai"

    def search_hit_ids(self):
        yield "1326083433"
        yield "13260"

    def search_miss_ids(self):
        yield "1326083433n"
        yield "123"

    def helper_set_name(self, row, name):
        row.set_name(name)

    def setUp(self):
        super().setUp()
        row = self.table(self.insert_id)
        self.helper_set_name(row, self.insert_name)
        self.db.add(row)
        self.db.commit()

    def test_search_name(self):
        self.assertTrue(self.insert_name in [r.get_name() for r in
                                             SearchHelper.search(self.db, self.table, self.name_col, self.insert_name)])
        for s in self.search_hit_names():
            with self.subTest(search=s):
                resp = SearchHelper.search(self.db, self.table, self.name_col, s)
                self.assertTrue(self.insert_name in [r.get_name() for r in resp])
        for s in self.search_miss_names():
            with self.subTest(search=s):
                resp = SearchHelper.search(self.db, self.table, self.name_col, s)
                self.assertFalse(self.insert_name in [r.get_name() for r in resp])

    def test_search_ids(self):
        self.assertTrue(self.insert_name in [r.get_name() for r in
                                             SearchHelper.search(self.db, self.table, self.id_col, str(self.insert_id))])
        for s in self.search_hit_ids():
            with self.subTest(search=s):
                resp = SearchHelper.search(self.db, self.table, self.id_col, s)
                self.assertTrue(self.insert_name in [r.get_name() for r in resp])
        for s in self.search_miss_ids():
            with self.subTest(search=s):
                resp = SearchHelper.search(self.db, self.table, self.id_col, s)
                self.assertFalse(self.insert_name in [r.get_name() for r in resp])


class TestSearchHelperCharacters2(TestSearchHelperCharacters):
    @property
    def insert_id(self):
        return 157809097

    @property
    def insert_name(self):
        return "Conman"

    def search_hit_names(self):
        yield "Conman"
        yield "conm"

    def search_miss_names(self):
        yield "Ta"
        yield "Ai"
        yield "Nat"
        yield "atu"

    def search_hit_ids(self):
        yield "157809097"
        yield "78090"
