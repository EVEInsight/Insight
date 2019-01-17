from tests.test_database.test_db_tables.test_eve import AbstractTableRowTesting, AbstractTestBase
from database.db_tables.eve import base_objects
from sqlalchemy.exc import InvalidRequestError
import unittest


class TestTableRow(AbstractTableRowTesting.AbstractTableRowTesting):
    @property
    def api_not_implemented(self):
        return True

    @property
    def helper_row(self):
        return base_objects.table_row

    def setUp(self):
        super(AbstractTestBase.AbstractTestBase, self).setUp()
        self.row = base_objects.table_row()

    def test_get_id(self):
        self.assertRaises(NotImplementedError, self.row.get_id)

    def test_primary_key_row(self):
        with self.assertRaises(NotImplementedError):
            self.row.primary_key_row()

    def test_get_row(self):
        with self.assertRaises(InvalidRequestError):
            self.helper_row.get_row(1, self.service)

    @unittest.SkipTest
    def test_load_fk_objects_merge(self):
        super().test_load_fk_objects_merge()

    @unittest.SkipTest
    def test_load_fk_objects_add(self):
        super().test_load_fk_objects_add()
