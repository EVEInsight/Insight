import networkx as nx
from sqlalchemy.orm import Session
from database.db_tables import *
import datetime


class RouteMapper(object):
    def __init__(self, service_object):
        self.service: service.service_module = service_object
        self.graph = nx.Graph()
        self.routes = {}
        self.load_vertices()
        self.load_edges()
        self.__load_all_routes()

    def load_vertices(self):
        db: Session = self.service.get_session()
        try:
            for v in [i.get_id() for i in db.query(tb_systems).all()]:
                self.graph.add_node(v)
                self.routes[v] = None
            print("Loaded {} vertices into route mapper".format(self.graph.number_of_nodes()))
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def load_edges(self):
        db: Session = self.service.get_session()
        try:
            for edge in db.query(tb_stargates).all():
                self.graph.add_edge(edge.system_from, edge.system_to)
            print("Loaded {} edges into route mapper".format(self.graph.number_of_edges()))
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def __load_all_routes(self):
        if self.service.cli_args.routes_all:
            start = datetime.datetime.utcnow()
            print("Starting route loader. This might take some time.")
            load_count = 0
            for s in self.routes.keys():
                load_count += len(self.__load_route(s))
            print("Loaded {:,} routes in {} seconds".format(load_count,
                                                            str((datetime.datetime.utcnow() - start).total_seconds())))
        else:
            print("Route information will cache on access by feed services.")

    def __load_route(self, system_id):
        if system_id is None:
            return None
        if self.routes.get(system_id) is None:
            try:
                self.routes[system_id] = nx.single_source_shortest_path_length(self.graph, system_id)
            except nx.NodeNotFound as ex:
                print(ex)
        return self.routes.get(system_id)

    def total_jumps(self, system_a: int, system_b: int):
        """returns total jumps between two system ids. returns none if no route exists"""
        return_val = None
        try:
            sysA = self.__load_route(system_a)
            if sysA is not None:
                return_val = sysA.get(system_b)
        except Exception as ex:
            print(ex)
        finally:
            return return_val


from . import service