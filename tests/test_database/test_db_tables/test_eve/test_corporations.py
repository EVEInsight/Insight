from unittest import TestCase
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from service.service import service_module
from database.db_tables import Base
from database.db_tables.eve import tb_corporations
from swagger_client import UniverseApi


class TestCharacters(TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.db = Session(self.engine)
        Base.Base.metadata.create_all(self.engine)
        self.db.add(tb_corporations(1326083433))
        self.db.add(tb_corporations(1363013499))
        self.db.commit()

    def tearDown(self):
        Base.Base.metadata.drop_all(self.engine)

    def helper_get_id(self, char_id: int)->tb_corporations:
        return self.db.query(tb_corporations).filter(tb_corporations.corporation_id == char_id).one()

    def test_get_id(self):
        self.assertEqual(self.helper_get_id(1326083433).get_id(), 1326083433)


