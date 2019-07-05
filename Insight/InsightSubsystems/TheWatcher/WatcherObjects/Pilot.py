from InsightSubsystems.TheWatcher.WatcherObjects import WatcherObject, SolarSystem
from database.db_tables import tb_characters, tb_attackers, tb_systems, tb_victims, tb_kills
import datetime
import InsightLogger


class Pilot(WatcherObject.WatcherObject):
    def __init__(self, sql_char, watcher_mod):
        super().__init__(watcher_mod)
        assert isinstance(sql_char, tb_characters)
        self.pilot_object: tb_characters = sql_char
        self.system: SolarSystem.SolarSystem = None
        self.ship_object: tb_attackers = None
        self.affiliation: tb_attackers = None
        self.km: tb_kills = None
        self.last_update = datetime.datetime.utcfromtimestamp(0)
        self.logger = InsightLogger.InsightLogger.get_logger("Watcher.Pilots.{}".format(self.id()),
                                                             "Watcher_Pilots.log", child=True)
        self.logger.info("Loaded new pilot.")
        self.index_check()

    def index_check(self):
        """ensures that the current pilot is in both the name and id tables in the watcher"""
        if self.id():
            if self.watcher.pilots_id.get(self.id()) is None:
                self.watcher.pilots_id[self.id()] = self
        if self.name():
            if self.watcher.pilots_name.get(self.name()) is None:
                self.watcher.pilots_name[self.name()] = self

    def _leave_system(self):
        """leave the system"""
        if self.system is not None:
            self.system.remove_pilot(self)
        self.system = None

    def _move_system(self, new_system):
        self._leave_system()
        if isinstance(new_system, tb_systems):
            self.system = self.watcher.get_system(new_system)
            if isinstance(self.system, SolarSystem.SolarSystem):
                self.system.add_pilot(self)
        else:
            self.system = None

    def _change_ships(self, new_ship):
        if isinstance(new_ship, tb_attackers):
            self.ship_object = new_ship
        else:
            self.ship_object = None

    def is_ship(self, involved_row) -> bool:
        try:
            # if involved_row.object_ship is None:  # incoming pod - update not always true
            #     return True
            if involved_row.object_ship.get_category() == 6:
                return True
            return False
        except Exception as ex:
            return False

    def is_alive_nonnpc(self, involved_row) -> bool:
        try:
            if involved_row.object_ship is None:  # not always true that this signals lost ship
                return True
            if involved_row.object_ship.group_id == 29:  # capsule check
                return False
            if involved_row.object_ship.get_category() != 6:
                return False
            return True
        except Exception as ex:
            print(ex)
            return False

    def _state_ischanged(self, mail_row, involved_row):
        new_time = mail_row.get_time()
        if new_time > self.last_update:
            self.affiliation = involved_row
        return new_time > self.last_update and self.is_ship(involved_row)

    def _state_isdead(self, involved_row):
        if isinstance(involved_row, tb_victims):
            return True
        else:
            return not self.is_alive_nonnpc(involved_row)

    def _set_involved_mail(self, mail_row):
        self.km = mail_row

    def _state_modify(self, mail_row, involved_row):
        self._set_involved_mail(mail_row)
        self.last_update = mail_row.get_time()
        if self._state_isdead(involved_row):
            self._change_ships(None)
            self._move_system(None)
        else:
            self._change_ships(involved_row)
            self._move_system(mail_row.get_system())

    def update_self(self, mail_row, involved_row):
        if self._state_ischanged(mail_row, involved_row):
            self._state_modify(mail_row, involved_row)

    def id(self):
        return self.pilot_object.get_id()

    def name(self) -> str:
        return self.pilot_object.get_name()

    def corp(self) -> str:
        if self.affiliation is not None:
            return self.affiliation.str_corp_name()
        else:
            return "Unknown"

    def alliance(self) -> str:
        if self.affiliation is not None:
            return self.affiliation.str_alliance_name()
        else:
            return "Unknown"

    def ship(self):
        if self.ship_object is not None:
            return self.ship_object.str_ship_name()
        else:
            return "Unknown"

    def time_delta(self) -> float:
        return round(((datetime.datetime.utcnow() - self.last_update).total_seconds() / 60), 1)

    def __str__(self):
        return self.name()

    def embed_row_str(self) -> str:
        return "{} -- {} ({}m)".format(self.name(), self.ship(), self.time_delta())

    def __eq__(self, other):
        if isinstance(other, int):
            return self.id() == other
        elif isinstance(other, Pilot):
            return self.id() == other.id()
        else:
            print("Invalid Pilot compare")
            return False

    def __hash__(self):
        return self.id()

    def km_id(self):
        if self.km is not None:
            return self.km.kill_id
        else:
            return None
