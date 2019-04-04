from tests.abstract import DatabaseTesting
from database.db_tables import SearchHelper, tb_types, tb_groups


class TestSearchHelperSystems(DatabaseTesting.DatabaseTesting):
    def setUp(self):
        super().setUp()
        self.import_type_group_category(self.engine, True)

    def test_search_type_group_is_ship_multi(self):
        with self.subTest("Type name"):
            self.assert_contains(SearchHelper.search_type_group_is_ship(self.db, "Drake"), tb_types, 24698)
        with self.subTest("Type id"):
            self.assert_contains(SearchHelper.search_type_group_is_ship(self.db, "24698"), tb_types, 24698)
        with self.subTest("Type and Group mixed result list"):
            r = SearchHelper.search_type_group_is_ship(self.db, "2")
            self.assertLess(200, len(r))
            self.assert_contains(r, tb_groups, 1527)  # logi frig
            self.assert_contains(r, tb_types, 20185)  # charon
