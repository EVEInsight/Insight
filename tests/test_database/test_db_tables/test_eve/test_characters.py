from unittest import TestCase
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from service.service import service_module
from database.db_tables import Base
from database.db_tables.eve import tb_characters
from swagger_client import UniverseApi


class TestCharacters(TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.db = Session(self.engine)
        Base.Base.metadata.create_all(self.engine)
        self.db.add(tb_characters(1326083433))
        self.db.add(tb_characters(1363013499))
        self.db.commit()

    def tearDown(self):
        Base.Base.metadata.drop_all(self.engine)

    def helper_get_id(self, char_id: int)->tb_characters:
        return self.db.query(tb_characters).filter(tb_characters.character_id == char_id).one()

    def test_get_id(self):
        self.assertEqual(self.helper_get_id(1326083433).get_id(), 1326083433)

    def test_set_name(self):
        self.helper_get_id(1326083433).set_name("Natuli")
        self.db.commit()
        self.assertEqual(self.helper_get_id(1326083433).get_name(), "Natuli")
        self.assertEqual(self.helper_get_id(1326083433).character_name, "Natuli")
        obj = tb_characters(157809097)
        self.assertEqual(obj.character_name, None)
        obj.set_name("C")
        self.assertEqual(obj.character_name, "C")

    def test_get_name(self):
        self.assertEqual(self.helper_get_id(1326083433).get_name(), None)
        self.helper_get_id(1326083433).set_name("Natuli")
        self.db.commit()
        self.assertEqual(self.helper_get_id(1326083433).get_name(), "Natuli")

    def test_need_name(self):
        self.helper_get_id(1363013499).set_name("Travis")
        self.db.commit()
        self.assertTrue(self.helper_get_id(1326083433).need_name)
        self.assertFalse(self.helper_get_id(1363013499).need_name)
        self.helper_get_id(1326083433).set_name("Natuli")
        self.db.commit()
        self.assertFalse(self.helper_get_id(1326083433).need_name)

    def test_primary_key_row(self):
        self.assertEqual(tb_characters.primary_key_row(), tb_characters.character_id)

    def test_make_row(self):
        obj = tb_characters.make_row(157809097)
        with self.assertRaises(NoResultFound):
            self.helper_get_id(157809097)
        self.db.add(obj)
        self.db.commit()
        self.assertIsInstance(self.helper_get_id(157809097), tb_characters)
        obj2 = tb_characters.make_row(157809097)
        obj2.character_name = "Name"
        self.db.merge(obj2)
        self.assertEqual(self.helper_get_id(157809097).character_name, "Name")

    def test_reset_name(self):
        r = self.helper_get_id(1326083433)
        r.character_name = "Natuli"
        self.db.commit()
        self.assertEqual(self.helper_get_id(1326083433).character_name, "Natuli")
        self.helper_get_id(1326083433).reset_name()
        self.db.commit()
        self.assertEqual(self.helper_get_id(1326083433).character_name, None)

    def test_get_api(self):
        self.assertIsInstance(tb_characters.get_api(tb_characters.get_configuration()), UniverseApi)
