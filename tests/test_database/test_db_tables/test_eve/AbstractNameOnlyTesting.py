from swagger_client import PostUniverseNames200Ok, UniverseApi
import random
from tests.test_database.test_db_tables.test_eve import AbstractTestBase


class AbstractNameOnlyTesting(AbstractTestBase.AbstractTestBase):

    def helper_get_response(self, api, **kwargs):
        """emulate overwritten method by child resolve id class"""
        return api.post_universe_names(**kwargs, datasource='tranquility')

    def test_make_row(self):
        self.assertIsInstance(self.helper_row.make_row(self.helper_assert_id), self.helper_row)

    def test_set_name(self):
        row = self.helper_get_row(self.helper_assert_id)
        row.set_name(self.helper_assert_name)
        self.assertEqual(row.get_name(), self.helper_assert_name)
        self.db.commit()
        self.assertEqual(self.helper_get_row(self.helper_assert_id).get_name(), self.helper_assert_name)

    def test_get_name(self):
        row = self.helper_get_row(self.helper_assert_id)
        row.set_name(self.helper_assert_name)
        self.assertEqual(row.get_name(), self.helper_assert_name)

    def test_reset_name(self):
        row = self.helper_get_row(self.helper_assert_id)
        row.set_name(self.helper_assert_name)
        self.assertNotEqual(row.get_name(), None)
        row.reset_name()
        self.assertEqual(row.get_name(), None)

    def test_need_name(self):
        self.assertTrue(self.helper_get_row(self.helper_assert_id).need_name)
        self.helper_get_row(self.helper_assert_id).set_name(self.helper_assert_name)
        self.db.commit()
        self.assertFalse(self.helper_get_row(self.helper_assert_id).need_name)

    def test_get_api(self):
        self.assertIsInstance(self.helper_row.get_api(self.helper_row.get_configuration()), UniverseApi)

    def test_get_response(self):
        resp = self.helper_get_response(self.helper_row.get_api(self.helper_row.get_configuration()), ids=[self.helper_assert_id])
        for r in resp:
            self.assertIsInstance(r, PostUniverseNames200Ok)
            self.assertIsInstance(r.to_dict(), dict)
            self.assertNotEqual(r.to_dict().get('id'), None)
            self.assertNotEqual(r.to_dict().get('name'), None)
            if r.id == self.helper_assert_id:
                self.assertEqual(self.helper_assert_id, r.id)
                self.assertEqual(self.helper_assert_name, r.name)
                return
        self.fail("Not found.")

    def test_missing_id_chunk_size(self):
        self.assertEqual(self.helper_row.missing_id_chunk_size(), 1000)

    def test_missing_name_objects(self):
        need_names = []
        have_names = []
        for row in self.db.query(self.helper_row).filter(self.helper_row.need_name==True).all():
            need_names.append(row)
        for row in self.db.query(self.helper_row).filter(self.helper_row.need_name==False).all():
            have_names.append(row)
        for i in range(1, 10):
            row = self.helper_row(i)
            if random.choice([True, False]):
                row.set_name("Testing")
                have_names.append(row)
            else:
                need_names.append(row)
            self.db.add(row)
        rows = self.helper_row.missing_name_objects(self.service)
        self.assertEqual(len(rows), len(need_names))
        for r in need_names:
            self.assertTrue(r.get_name() in [i.get_name() for i in need_names])

    def test_split_lists(self):
        items = [i for i in range(0, 3500)]
        iteration = 0
        for i in self.helper_row.split_lists(items, self.helper_row.missing_id_chunk_size()):
            if iteration < 3:
                self.assertEqual(len(i), self.helper_row.missing_id_chunk_size())
            else:
                self.assertEqual(len(i), 500)
                return
            iteration += 1

