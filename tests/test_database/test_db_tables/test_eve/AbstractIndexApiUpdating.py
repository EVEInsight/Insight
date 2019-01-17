from tests.abstract import DatabaseTesting
from swagger_client import UniverseApi
from urllib3._collections import HTTPHeaderDict


class AbstractIndexApiUpdating(DatabaseTesting.DatabaseTesting):
    @property
    def index_id_file_name(self):
        raise NotImplementedError
        # return "categories.txt"

    @property
    def table_row(self):
        raise NotImplementedError
        # return tb_category

    def setUp(self):
        super().setUp()
        self.set_resource_path("db_tables", "eve", "indexes")
        self.ids = [int(i) for i in self.get_file_lines(self.index_id_file_name)]

    def test_api_import_all_ids(self):
        self.table_row.api_import_all_ids(self.service)
        item_ids = [r.get_id() for r in self.db.query(self.table_row).all()]
        for assert_id in self.ids:
            with self.subTest(id=assert_id):
                self.assertTrue(assert_id in item_ids)

    def test_index_swagger_api_call(self):
        items = self.table_row.index_swagger_api_call(self.table_row._index_get_api(self.table_row.get_configuration()), datasource='tranquility')
        self.assertIsInstance(items, tuple)
        self.assertIsInstance(items[0], list)
        self.assertIsInstance(items[2], HTTPHeaderDict)
        for i in items[0]:
            with self.subTest(id=i):
                self.assertTrue(i in self.ids)

    def test__index_get_api(self):
        self.assertIsInstance(self.table_row._index_get_api(self.table_row.get_configuration()), UniverseApi)

    # def test__index_get_response(self):
    #     return # helper function used by api_import_all_ids, no need to retest again
