from .base_objects import *
from . import systems, attackers, victims, locations, types
from dateutil.parser import parse as dateTimeParser
from functools import cmp_to_key
import operator


class Kills(dec_Base.Base, table_row):
    __tablename__ = 'kills'

    kill_id = Column(Integer,primary_key=True, nullable=False, autoincrement=False)
    killmail_time = Column(DateTime,default=None,nullable=True)
    solar_system_id = Column(Integer, ForeignKey("systems.system_id"), default=None, nullable=True)
    locationID = Column(Integer,ForeignKey("locations.location_id"),default=None,nullable=True)
    hash = Column(String,default=None,nullable=True)
    fittedValue = Column(Float,default=0.0,nullable=False)
    totalValue = Column(Float,default=0.0,nullable=False)
    points = Column(Float,default=0.0,nullable=False)
    npc = Column(Boolean,default=False,nullable=False)
    solo = Column(Boolean,default=False,nullable=False)
    awox = Column(Boolean, default=False,nullable=False)
    href = Column(String,default=None,nullable=True)
    loaded_time = Column(DateTime,default=datetime.datetime.utcnow(),nullable=False)

    object_system: systems.Systems = relationship("Systems", uselist=False, back_populates="object_kills_in_system",lazy="joined")
    object_attackers: List[attackers.Attackers] = relationship("Attackers",uselist=True,back_populates="object_kill",lazy="joined")
    object_victim: victims.Victims = relationship("Victims",uselist=False,back_populates="object_kill",lazy="joined")
    object_location: locations.Locations = relationship("Locations",uselist=False, back_populates="object_kills_at_location",lazy="joined")

    def __init__(self, data: dict):
        self.loaded_time = datetime.datetime.utcnow()
        self.kill_id = data.get("killID")
        killmail_dict = data.get("killmail")
        if killmail_dict:
            self.killmail_time = dateTimeParser(killmail_dict.get("killmail_time"))
            self.solar_system_id = killmail_dict.get("solar_system_id")
        zkb_dict = data.get("zkb")
        if zkb_dict:
            self.locationID = zkb_dict.get("locationID")
            self.hash = zkb_dict.get("hash")
            self.fittedValue = zkb_dict.get("fittedValue")
            self.totalValue = zkb_dict.get("totalValue")
            self.points = zkb_dict.get("points")
            self.npc = zkb_dict.get("npc")
            self.solo = zkb_dict.get("solo")
            self.awox = zkb_dict.get("awox")
            self.href = zkb_dict.get("href")
        self.dict_attackers = killmail_dict.get("attackers") if killmail_dict else None
        self.dict_victim = killmail_dict.get("victim") if killmail_dict else None

    def load_fk_objects(self):
        if self.solar_system_id:
            self.object_system = systems.Systems(self.solar_system_id)
        if self.locationID:
            self.object_location = locations.Locations(self.locationID)
        if self.dict_attackers:
            for attacker in self.dict_attackers:
                self.object_attackers.append(attackers.Attackers(attacker))
        if self.dict_victim:
            self.object_victim = victims.Victims(self.dict_victim)

    def compare_value(self, filter):
        try:
            if filter.min is None and filter.max is None:
                return True
            elif filter.min is not None and filter.max is not None:
                return filter.min <= self.totalValue <= filter.max
            elif filter.min is not None and filter.max is None:
                return self.totalValue >= filter.min
            elif filter.min is None and filter.max is not None:
                return self.totalValue <= filter.max
            else:
                return False
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def primary_key_row(cls):
        return cls.kill_id

    @classmethod
    def make_row(cls, data, service_module):
        id = data.get("killID")
        if id:
            db: Session = service_module.get_session()
            try:
                __row = db.query(cls).filter(cls.primary_key_row() == id).one()
                return None
            except NoResultFound:
                __row = cls(data)
                __row.load_fk_objects()
                service_module.get_session().merge(__row)
                return __row
        else:
            return None

    @classmethod
    def get_row(cls, data, service_module):
        db:Session = service_module.get_session()
        return db.query(cls).filter(cls.primary_key_row() == data.get("killID")).one()

    def get_highest_attacker(self, attackers_list):
        top_attacker: attackers.Attackers = attackers_list[0]
        for a in attackers_list:
            if a.compare_ship_value(top_attacker):
                top_attacker = a
        return top_attacker

    def str_overview_attacking_capitals(self, attackers_list):
        ship_totals = []
        ships = [i.object_ship for i in attackers_list]
        for ship in list(set(ships)):
            ship_totals.append((ship.type_name, ships.count(ship)))
        ship_totals.sort(key=operator.itemgetter(1), reverse=True)
        ships_str = ""
        for s in ship_totals:
            ships_str += "{0:<20}   {1}\n".format(str(s[0]), str(s[1]))
        return ships_str

    def filter_loss(self, filter_list=[], using_blacklist=False):
        """whitelist - True=in filter_list, False=not in filter list
        blacklist - True=not in filter_list, False=in filter list"""
        for filter in filter_list:
            if self.object_victim.compare_filter_list(filter):
                if using_blacklist:
                    return False
                else:
                    return True
        return True if using_blacklist else False

    def filter_system_ly(self, filter_list=[], using_blacklist=False):
        """whitelist - returns the first system within range, otherwise returns None if no systems in filter are within ly range
        blacklist - returns KM system if it is not within range of any systems in the BL otherwise returns none"""
        for system in filter_list:
            if self.object_system.compare_range(system):
                if not using_blacklist:
                    return system.object_item
                else:
                    return None
        return None if not using_blacklist else self.object_system

    def filter_system(self, filter_list=[], using_blacklist=False):
        """whitelist - returns True if in filter, otherwise False
        blacklist - returns False if km system matches anything in filters, else True"""
        for system_reg in filter_list:
            if self.object_system.compare_filter(system_reg):
                if not using_blacklist:
                    return True
                else:
                    return False
        return False if not using_blacklist else True

    def filter_attackers(self, attacker_list: List[attackers.Attackers], filter_list=[], using_blacklist=False):
        """return a list of attackers filtered using either a blacklist or whitelist
        whitelist - attacker must be in whitelist otherwise not returned
        blacklist - attacker must not be in blacklist otherwise returned"""
        return_list: List[attackers.Attackers] = []
        for a in attacker_list:
            if any(a.compare_filter_list(f) for f in filter_list):
                if not using_blacklist:
                    return_list.append(a)
            else:
                if using_blacklist:
                    return_list.append(a)
        return list(set(return_list))

    def filter_victim(self,victim:victims.Victims,filter_list=[],using_blacklist=False):
        __return_item = None
        if victim is not None:
            if any(victim.compare_filter_list(f) for f in filter_list):
                if not using_blacklist:
                    __return_item = victim
            else:
                if using_blacklist:
                    __return_item = victim
        return __return_item

    def get_final_blow(self):
        for i in self.object_attackers:
            if i.final_blow == True:
                return i
        return None

    def get_attacker_count(self)->int:
        return len(self.object_attackers)

    def victim_pilotID(self):
        try:
            return str(self.object_victim.character_id)
        except:
            return ""

    def victim_pilotName(self):
        try:
            return str(self.object_victim.object_pilot.character_name)
        except:
            return ""

    def victim_corpName(self):
        try:
            return str(self.object_victim.object_corp.corporation_name)
        except:
            return ""

    def victim_allianceName(self):
        try:
            return str(self.object_victim.object_alliance.alliance_name)
        except:
            return ""

    def victim_totalDamage(self):
        try:
            return str("{:,d}".format(int(self.object_victim.damage_taken)))
        except:
            return ""

    def victim_iskLost(self):
        try:
            val = self.totalValue
            if val >= 1000000000:
                num = float(val / 1000000000)
                return '{:.2f}b'.format(num)
            elif val >= 1000000:
                num = float(val / 1000000)
                return '{:.2f}m'.format(num)
            else:
                num = float(val / 10000)
                return '{:.2f}k'.format(num)
        except:
            return ""

    def systemName(self):
        try:
            return str(self.object_system.name)
        except:
            return ""

    def regionName(self):
        try:
            return str(self.object_system.object_constellation.object_region.name)
        except:
            return ""

    def fb_pID(self,final_blow:attackers.Attackers):
        try:
            return str(final_blow.character_id)
        except:
            return ""

    def fb_ship(self,final_blow:attackers.Attackers):
        try:
            return str(final_blow.object_ship.type_name)
        except:
            return ""

    def fb_ShipGroup(self, attacker_: attackers.Attackers):
        try:
            return str(attacker_.object_ship.object_group.name)
        except:
            return ""

    def fb_Name(self,final_blow:attackers.Attackers):
        try:
            return str(final_blow.object_pilot.character_name)
        except:
            return ""

    def fb_Corp(self,final_blow:attackers.Attackers):
        try:
            return str(final_blow.object_corp.corporation_name)
        except:
            return ""

    def fb_Alliance(self, attacker_: attackers.Attackers, brackets=False):
        try:
            return str(attacker_.object_alliance.alliance_name) if not brackets else "({})".format(
                str(attacker_.object_alliance.alliance_name))
        except:
            return ""

    def str_attacker_count(self):
        count = self.get_attacker_count()
        if count == 1:
            return "solo"
        else:
            return "and **{}** others".format(str(count-1))

    def str_minutes_ago(self, text_mituntes_ago=False):
        try:
            minutes_ago = round(((datetime.datetime.utcnow() - self.killmail_time).total_seconds() / 60), 1)
            return str(minutes_ago) + " m/ago" if not text_mituntes_ago else str(minutes_ago) + " minutes ago"
        except:
            return ""

    def str_ly_range(self, other_system):
        try:
            return "{0:.2f}".format(self.object_system.ly_range(other_system))
        except:
            return ""

    def str_location_name(self):
        try:
            return " near **{}**.".format(
                str(self.object_location.name)) if self.object_location.name is not None else "."
        except:
            return "."
