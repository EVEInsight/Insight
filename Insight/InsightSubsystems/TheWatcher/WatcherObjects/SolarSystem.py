from InsightSubsystems.TheWatcher.WatcherObjects import WatcherObject, Pilot
from database.db_tables import tb_systems
import InsightLogger


class SolarSystem(WatcherObject.WatcherObject):
    def __init__(self, sql_object, watcher_mod):
        super().__init__(watcher_mod)
        assert isinstance(sql_object, tb_systems)
        self.system_object: tb_systems = sql_object
        self.pilots = {}
        self.logger = InsightLogger.InsightLogger.get_logger("Watcher.Systems.{}".format(self.id()),
                                                             "Watcher_Systems.log", child=True)
        self.logger.info("Loaded new system.")
        self.index_check()

    def index_check(self):
        """ensures that the current system is in both the name and id tables of the watcher"""
        if self.id():
            if self.watcher.systems_id.get(self.id()) is None:
                self.watcher.systems_id[self.id()] = self
        if self.name():
            if self.watcher.systems_name.get(self.name()) is None:
                self.watcher.systems_name[self.name()] = self

    def remove_pilot(self, pilot):
        assert isinstance(pilot, Pilot.Pilot)
        self.pilots.pop(pilot, None)
        self.logger.info("{} left system: {}".format(pilot, str(self.system_object)))

    def add_pilot(self, pilot):
        assert isinstance(pilot, Pilot.Pilot)
        self.pilots[pilot] = pilot
        self.logger.info("{} entered system: {} with ship: {} {} minutes ago.".format(pilot, self.system_object,
                                                                                      pilot.ship(), pilot.time_delta()))

    def id(self):
        return self.system_object.get_id()

    def name(self):
        return self.system_object.get_name()

    def __eq__(self, other):
        if isinstance(other, int):
            return self.id() == other
        elif isinstance(other, SolarSystem):
            return self.id() == other.id()
        else:
            print("Invalid Solar System compare")
            return False

    def __hash__(self):
        return self.id()
