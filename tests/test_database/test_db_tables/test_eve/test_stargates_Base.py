from tests.test_database.test_db_tables.test_eve import AbstractTableRowTesting, AbstractTestBase
from database.db_tables.eve import tb_stargates, tb_systems
from swagger_client import UniverseApi


class TestStargatesBase(AbstractTableRowTesting.AbstractTableRowTesting):
    @property
    def api_not_implemented(self):
        return False

    @property
    def helper_row(self):
        return tb_stargates

    @property
    def helper_assert_api_category(self):
        return UniverseApi

    def setUp(self):
        super(AbstractTestBase.AbstractTestBase, self).setUp()
        self.row = tb_stargates(1, 2)
        self.db.add(self.row)
        self.db.commit()

    def set_foreign_keys(self, tb_row: tb_stargates):
        return

    def helper_assert_foreign_keys(self, response_row):
        self.assertIsInstance(response_row.object_system_from, tb_systems)
        self.assertIsInstance(response_row.object_system_to, tb_systems)

    def test_get_id(self):
        with self.assertRaises(NotImplementedError):
            self.row.get_id()

    def test_get_row(self):
        with self.assertRaises(NotImplementedError):
            tb_stargates.get_row(1, self.service)

    def test_primary_key_row(self):
        with self.assertRaises(NotImplementedError):
            tb_stargates.primary_key_row()

    def test_load_fk_objects_merge(self):
        row = self.helper_row(5, 6)
        self.set_foreign_keys(row)
        row.load_fk_objects()
        self.db.merge(row)
        self.db.commit()
        self.helper_assert_foreign_keys(
            self.db.query(tb_stargates).filter(tb_stargates.system_from == 5, tb_stargates.system_to == 6).one())

    def test_load_fk_objects_add(self):
        row = self.helper_row(5, 6)
        self.set_foreign_keys(row)
        row.load_fk_objects()
        self.db.add(row)
        self.db.commit()
        self.helper_assert_foreign_keys(
            self.db.query(tb_stargates).filter(tb_stargates.system_from == 5, tb_stargates.system_to == 6).one())
