from tests.abstract import DatabaseTesting
from service import RouteMapper


class TestRouteMapperSolarSystem(DatabaseTesting.DatabaseTesting):
    def setUp(self):
        super().setUp()
        self.rm = RouteMapper.RouteMapper(self.service)
        self.s1 = RouteMapper.SolarSystem(self.rm, 10001, 1, 2, 3)
        self.s2 = RouteMapper.SolarSystem(self.rm, 10002, 2, 3, 4)
        self.rm.graph.add_node(self.s1)
        self.rm.graph.add_node(self.s2)
        self.rm.graph.add_edge(10001, 10002)

    def test_free_memory(self):
        self.s1._gate_distances = {10002: 1}
        self.s1._access_counter = 6
        self.s1.free_memory()
        self.assertEquals({10002: 1}, self.s1._gate_distances)
        self.s1._access_counter = 3
        self.s1.free_memory()
        self.assertEquals({}, self.s1._gate_distances)

    def test_load_gate_distances(self):
        self.s1.load_gate_distances()
        self.assertEquals(1, self.s1._gate_distances.get(10002))

    def test_has_gate_distances(self):
        self.s1._gate_distances = {}
        self.assertFalse(self.s1.has_gate_distances())
        self.s1._gate_distances = {1: 1}
        self.assertTrue(self.s1.has_gate_distances())

    def test_get_distance(self):
        self.assertEquals(1, self.s1.get_gate_distance(self.s2))
        self.assertEquals(1, self.s1._access_counter)

    def test_get_gate_distance(self):
        self.assertEqual(1, self.s1.get_gate_distance(self.s2))
        self.assertEqual(1, self.s2.get_gate_distance(self.s1))
        if self.s1.has_gate_distances():
            self.assertEqual(2, len(self.s1._gate_distances))
            self.assertEqual(0, len(self.s2._gate_distances))
            self.assertEquals(2, self.s1._access_counter)
            self.assertEquals(0, self.s2._access_counter)
        else:
            self.assertEqual(0, len(self.s1._gate_distances))
            self.assertEqual(2, len(self.s2._gate_distances))
            self.assertEquals(0, self.s1._access_counter)
            self.assertEquals(2, self.s2._access_counter)

    def test_eq(self):
        self.assertFalse(self.s1 == self.s2)
        self.assertTrue(self.s1 == self.s1)
        self.assertTrue(self.s1 == RouteMapper.SolarSystem(self.rm, 10001, 5, 6, 7))

    def test_hash(self):
        self.assertEqual(10001, hash(self.s1))
        self.assertEqual(10002, hash(self.s2))
