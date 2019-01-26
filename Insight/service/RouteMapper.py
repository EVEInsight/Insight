import networkx as nx
from sqlalchemy.orm import Session
from database.db_tables import *
import datetime
import random
import sys


class SolarSystem(object):
    def __init__(self, rm, system_id, x, y, z):
        self.id = system_id
        self.rm: RouteMapper = rm
        self.x = x
        self.y = y
        self.z = z
        self._gate_distances = {}
        self._access_counter = 0

    def free_memory(self):
        """if the system has been accessed less than 5 times, free its memory"""
        if 5 >= self._access_counter:
            self._gate_distances = {}
            self._access_counter = 0

    def load_gate_distances(self):
        try:
            if not self.has_gate_distances():
                self._gate_distances = nx.single_source_shortest_path_length(self.rm.graph, self)
        except Exception as ex:
            print(ex)

    def has_gate_distances(self):
        """if empty check"""
        return bool(self._gate_distances)

    def get_distance(self, other):
        if not self.has_gate_distances():
            self.load_gate_distances()
        self._access_counter += 1
        return self._gate_distances.get(other)

    def get_gate_distance(self, other):
        return_val = None
        try:
            if self.has_gate_distances():
                return_val = self.get_distance(other)
            elif other.has_gate_distances():
                return_val = other.get_distance(self)
            else:
                if random.choice([True, False]):
                    return_val = self.get_distance(other)
                else:
                    return_val = other.get_distance(self)
        except Exception as ex:
            print(ex)
        finally:
            return return_val

    def __eq__(self, other):
        if isinstance(other, int):
            return self.id == other
        elif isinstance(other, SolarSystem):
            return self.id == other.id
        else:
            return False

    def __hash__(self):
        return self.id


class RouteMapper(object):
    def __init__(self, service_object):
        self.service: service.service_module = service_object
        self.graph = nx.Graph()
        self.systems = {}
        self._next_memory_free = datetime.datetime.utcnow()

    def _memfree(self):
        """frees underutilized memory from the system table"""
        try:
            if datetime.datetime.utcnow() >= self._next_memory_free:
                self._next_memory_free = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                for s in self.systems.values():
                    s.free_memory()
        except Exception as ex:
            print(ex)

    def _load_vertices(self):
        db: Session = self.service.get_session()
        try:
            for row in db.query(tb_systems).all():
                if row.get_id() is not None:
                    s = SolarSystem(self, row.get_id(), row.pos_x, row.pos_y, row.pos_z)
                    self.graph.add_node(s)
                    self.systems[s] = s
            print("Loaded {} vertices into route mapper".format(self.graph.number_of_nodes()))
        except Exception as ex:
            print(ex)
            print("Error when loading map vertices.")
            sys.exit(1)
        finally:
            db.close()

    def _load_edges(self):
        db: Session = self.service.get_session()
        try:
            for edge in db.query(tb_stargates).all():
                self.graph.add_edge(edge.system_from, edge.system_to)
            print("Loaded {} edges into route mapper".format(self.graph.number_of_edges()))
        except Exception as ex:
            print(ex)
            print("Error when loading map edges.")
            sys.exit(1)
        finally:
            db.close()

    def total_jumps(self, system_a: int, system_b: int):
        """returns total jumps between two system ids. returns none if no route exists"""
        return_val = None
        try:
            syaA: SolarSystem = self.systems.get(system_a)
            sysB: SolarSystem = self.systems.get(system_b)
            if syaA is not None and sysB is not None:
                return_val = syaA.get_gate_distance(sysB)
            self._memfree()
        except Exception as ex:
            print(ex)
        finally:
            return return_val

    def setup_load(self):
        self._load_vertices()
        self._load_edges()


from . import service
