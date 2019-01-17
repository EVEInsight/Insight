from swagger_client import Configuration
import random
from tests.test_database.test_db_tables.test_eve import AbstractTestBase


class AbstractTableRowTesting(AbstractTestBase.AbstractTestBase):
    @property
    def api_not_implemented(self):
        raise NotImplementedError
        # return True

    def helper_set_name_row(self, row, name):
        raise NotImplementedError
        # row.name = name

    def helper_get_name(self, tb_row):
        raise NotImplementedError
        # return tb_row.name

    def set_foreign_keys(self, row):
        raise NotImplementedError
        # row.constellation_id = 20000153

    def helper_assert_foreign_keys(self, row):
        raise NotImplementedError

    def test_get_id(self):
        self.assertEqual(self.helper_get_row(self.helper_assert_id).get_id(), self.helper_assert_id)

    def test_load_fk_objects_merge(self):
        row_id = random.randint(1000, 2000)
        row = self.helper_row(row_id)
        self.set_foreign_keys(row)
        row.load_fk_objects()
        self.db.merge(row)
        self.db.commit()
        self.helper_assert_foreign_keys(self.helper_get_row(row_id))

    def test_load_fk_objects_add(self):
        row_id = random.randint(1000, 2000)
        row = self.helper_row(row_id)
        self.set_foreign_keys(row)
        row.load_fk_objects()
        self.db.add(row)
        self.db.commit()
        self.helper_assert_foreign_keys(self.helper_get_row(row_id))

    def test_get_configuration(self):
        self.assertIsInstance(self.helper_row.get_configuration(), Configuration)

    def test_get_api(self):
        try:
            self.helper_row.get_api(self.helper_row.get_configuration())
        except Exception as ex:
            if isinstance(ex, NotImplementedError):
                if not self.api_not_implemented:
                    self.fail("Expected implementation but got not implemented error.")
            else:
                if self.api_not_implemented:
                    self.fail("Expected not implemented but function was implemented.")

    def test_get_response(self):
        try:
            self.helper_row.get_response(self.helper_row.get_api(self.helper_row.get_configuration()))
        except Exception as ex:
            if isinstance(ex, NotImplementedError):
                if not self.api_not_implemented:
                    self.fail("Expected implementation but got not implemented error.")
            else:
                if self.api_not_implemented:
                    self.fail("Expected not implemented but function was implemented.")

    def test_primary_key_row(self):
        self.assertEqual(self.helper_row.primary_key_row(), self.helper_pk)

    def test_get_row(self):
        row = self.helper_row.get_row(self.helper_assert_id, self.service)  # get existing
        self.assertEqual(row.get_id(), self.helper_assert_id)
        self.assertEqual(self.helper_get_name(row), None)
        self.helper_set_name_row(row, self.helper_assert_name)
        self.db.commit()
        row = self.helper_row.get_row(self.helper_assert_id, self.service)
        self.assertEqual(self.helper_get_name(row), self.helper_assert_name)

        new_id = random.randint(2, 1000)
        new_row = self.helper_row.get_row(new_id, self.service)
        self.assertEqual(new_row.get_id(), new_id)
        self.assertEqual(self.helper_get_name(new_row), None)
        self.db.add(new_row)
        self.helper_set_name_row(new_row, "Test")
        self.db.commit()
        new_row = self.helper_row.get_row(new_id, self.service)
        self.assertEqual(new_row.get_id(), new_id)
        self.assertEqual(self.helper_get_name(new_row), "Test")
