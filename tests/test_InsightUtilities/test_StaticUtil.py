from unittest import TestCase
from InsightUtilities import StaticUtil


class TestStaticUtil(TestCase):
    def test_filter_type(self):
        r = ["test", 1, 2, 3, 4, 5, "demo"]
        self.assertEqual(["test", "demo"], StaticUtil.filter_type(r, str))
        self.assertEqual([1, 2, 3, 4, 5], StaticUtil.filter_type(r, int))

    def test_filter_type_same_mem(self):
        r = [1, 2]
        self.assertEqual(id(r[0]), id(StaticUtil.filter_type(r, int)[0]))