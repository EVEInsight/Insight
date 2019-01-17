from tests.test_database.test_db_tables.test_eve import AbstractIndexApiUpdating
from database.db_tables.eve import tb_types
import unittest


class TestTypesIndex(AbstractIndexApiUpdating.AbstractIndexApiUpdating):
    @property
    def index_id_file_name(self):
        return "types.txt"

    @property
    def table_row(self):
        return tb_types

    @unittest.SkipTest  # too many pages, long test
    def test_api_import_all_ids(self):
        super().test_api_import_all_ids()
