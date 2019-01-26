from tests.abstract import DatabaseTesting
from service import RouteMapper
from tests.mocks import ServiceModule
import unittest
import datetime


class TestRouteMapper(DatabaseTesting.DatabaseTesting):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.engine = cls.get_engine()
        cls.scoped_session = cls.get_scoped_session(cls.engine)
        cls.import_systems(cls.engine)
        cls.import_stargates(cls.engine)
        cls.route_mapper = RouteMapper.RouteMapper(ServiceModule.ServiceModule(cls.scoped_session))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.metadata_drop_all(cls.engine)

    def setUp(self):
        self.resources = self.get_resource_path("service", "RouteMapper", path=None)

    def tearDown(self):
        return

    def test__memfree(self):
        s = RouteMapper.SolarSystem(self.route_mapper, 10, 1, 1, 1)
        self.route_mapper.systems[1] = s
        s._gate_distances = {1: 1}
        s._access_counter = 6
        self.route_mapper._memfree()
        self.assertEqual({1: 1}, s._gate_distances)
        self.assertEqual(6, s._access_counter)
        self.route_mapper._memfree()
        self.assertEqual({1: 1}, s._gate_distances)
        self.assertEqual(6, s._access_counter)
        s._access_counter = 1
        self.route_mapper._next_memory_free = datetime.datetime.utcnow()
        self.route_mapper._memfree()
        self.assertEqual({}, s._gate_distances)
        self.assertEqual(0, s._access_counter)

    def test_01_load_vertices(self):
        self.route_mapper._load_vertices()
        self.assertEqual(8285, self.route_mapper.graph.number_of_nodes())  # number of systems
        self.assertEqual(0, self.route_mapper.graph.number_of_edges())  # number of actual stargates
        self.assertEqual(0, self.route_mapper.graph.number_of_selfloops())

    def test_02_load_edges(self):
        self.route_mapper._load_vertices()
        self.route_mapper._load_edges()
        self.assertEqual(8285, self.route_mapper.graph.number_of_nodes())
        self.assertEqual(6913, self.route_mapper.graph.number_of_edges())  # after edges are loaded
        self.assertEqual(0, self.route_mapper.graph.number_of_selfloops())

    def test_03_total_jumps(self):
        """this function tests the distances between multiple systems found in the assert files"""
        for route in self.iterate_assert_file("routes_test.txt", "routes_assert.txt"):
            sys1 = int(route[0].split()[0])
            sys2 = int(route[0].split()[1])
            route_length = int(route[1])
            if route_length < 0:
                route_length = None
            with self.subTest(start=sys1, dest=sys2, jumps=route_length):
                self.assertEqual(route_length, self.route_mapper.total_jumps(sys1, sys2))
                self.assertEqual(route_length, self.route_mapper.total_jumps(sys2, sys1))

    @unittest.SkipTest
    def test_setup_load(self):  # not needed as this is just a helper function that calls load_vert abd load_edges
        self.fail()
