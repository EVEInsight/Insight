from sqlalchemy.orm.exc import NoResultFound
from tests.abstract import DatabaseTesting
from database.db_tables.eve import tb_corporations
from swagger_client import UniverseApi


class TestCorporations(DatabaseTesting.DatabaseTesting):
    def setUp(self):
        super().setUp()
        self.db.add(tb_corporations(1326083433))
        self.db.add(tb_corporations(1363013499))
        self.db.commit()

    def helper_get_id(self, char_id: int)->tb_corporations:
        return self.db.query(tb_corporations).filter(tb_corporations.corporation_id == char_id).one()

    def test_get_id(self):
        self.assertEqual(self.helper_get_id(1326083433).get_id(), 1326083433)


