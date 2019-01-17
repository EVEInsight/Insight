from tests.abstract import DatabaseTesting
from database.db_tables.eve import tb_characters
from swagger_client import PostUniverseNames200Ok
import random


class CharactersTestNameOnly(DatabaseTesting.DatabaseTesting):
    def setUp(self):
        super().setUp()
        self.set_resource_path('db_tables', 'eve', 'characters')
        self.id_lines = self.get_file_lines('pilot_ids250.txt')
        for char_ids in self.id_lines:
            self.db.add(tb_characters(int(char_ids)))
        self.db.commit()

    def test_make_row(self):
        self.db.add(tb_characters.make_row(1326083433))
        self.db.commit()
        self.assertIsInstance(self.db.query(tb_characters).filter(tb_characters.character_id == 1326083433).one(),
                              tb_characters)

    def test_set_name(self):
        for r in self.db.query(tb_characters).all():
            self.assertEqual(r.character_name, None)
            r.set_name(self.random_string(1, 240, True))
            self.assertNotEqual(r.character_name, None)
        self.db.commit()
        self.db.close()
        for r in self.db.query(tb_characters).all():
            self.assertNotEqual(r.character_name, None)

    def test_get_name(self):
        row = tb_characters(123)
        row.character_name = "Name"
        self.assertEqual(row.get_name(), "Name")

    def test_reset_name(self):
        for r in self.db.query(tb_characters).all():
            r.character_name = self.random_string(1, 240, True)
            self.assertNotEqual(r.character_name, None)
            r.reset_name()
            self.assertEqual(r.character_name, None)

    def test_get_response(self):
        resp = tb_characters.get_response(tb_characters.get_api(tb_characters.get_configuration()), ids=self.id_lines)
        for r in resp:
            self.assertIsInstance(r, PostUniverseNames200Ok)
            self.assertIsInstance(r.to_dict(), dict)
            self.assertNotEqual(r.to_dict().get('id'), None)
            self.assertNotEqual(r.to_dict().get('name'), None)

    def test_missing_id_chunk_size(self):
        self.assertEqual(tb_characters.missing_id_chunk_size(), 1000)

    def test_missing_name_objects(self):
        self.assertEqual(len(self.id_lines), len(tb_characters.missing_name_objects(self.service)))

    def test_split_lists(self):
        item_count = random.randint(1500, 2000)
        items = [0 for i in range(item_count)]
        total_loops = 0
        for i in tb_characters.split_lists(items, tb_characters.missing_id_chunk_size()):
            if total_loops >= 2:
                self.fail()
            elif total_loops == 1:
                self.assertEqual(len(i), item_count - 1000)
            else:
                self.assertEqual(len(i), 1000)
            total_loops += 1
