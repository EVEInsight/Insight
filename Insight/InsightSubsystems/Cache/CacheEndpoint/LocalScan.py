from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
from InsightUtilities.StaticHelpers import *
from datetime import datetime
from statistics import mean
from dateutil.parser import parse as dateTimeParser
from operator import itemgetter


class BucketManagerEntity(object):
    def __init__(self, name):
        self.name = name
        self.ships = {}
        self.ship_delays = {}
        self.locations = {}
        self.systems = {}
        self.mails = {}
        self.total = 0
        self.alive = 0
        self.dead = 0

    def add_ship(self, ship_name: str, seconds_ago: float, system_data: dict, location_data: dict, km_data: dict,
                 is_attacker: bool):
        ship_counts = self.ships.setdefault(ship_name, {"ship": ship_name, "alive": 0, "lost": 0, "total": 0, "avgSeconds": 0})
        ship_delays: list = self.ship_delays.setdefault(ship_name, [])
        ship_delays.append(seconds_ago)
        self.total += 1
        if is_attacker:
            ship_counts["alive"] += 1
            self.alive += 1
        else:
            if ship_name != "UNKNOWN":
                ship_counts["lost"] += 1
                self.dead += 1
            else:
                ship_counts["alive"] += 1
                self.alive += 1
        ship_counts["total"] += 1
        if location_data:
            loc_id = Helpers.get_nested_value(location_data, 0, "location_id")
            locations = self.locations.setdefault(loc_id, {"location": location_data, "total": 0})
            locations["total"] += 1
        if system_data:
            system_id = Helpers.get_nested_value(system_data, 0, "system_id")
            s = self.systems.setdefault(system_id, {"system": system_data, "total": 0})
            s["total"] += 1
        if km_data:
            km_id = Helpers.get_nested_value(system_data, 0, "killmail_id")
            k = self.systems.setdefault(km_id, {"km": km_data, "total": 0})
            k["total"] += 1

    def get_sorted_ships(self) -> list:
        tmp_ship_list = []
        for k, v in self.ships.items():
            avg_delay = mean(self.ship_delays[k]) if len(self.ship_delays[k]) else 0
            v["avgSeconds"] = avg_delay
            tmp_ship_list.append(v)
        return sorted(tmp_ship_list, key=itemgetter("total"), reverse=True)

    def get_top_dict(self, counttracking_dict):
        if len(counttracking_dict) == 0:
            return None
        else:
            d = max(counttracking_dict.values(), key=itemgetter("total"))
            d["ratio"] = d["total"] / self.total
            return d

    def to_dict(self) -> dict:
        return_dict = {
            "name": self.name,
            "ships": self.get_sorted_ships(),
            "systemHighestRatio": self.get_top_dict(self.systems),
            "locationHighestRatio": self.get_top_dict(self.locations),
            "kmHighestRatio": self.get_top_dict(self.mails),
            "alive": self.alive,
            "dead": self.dead,
            "total": self.total
        }
        return return_dict


class LocalScan(AbstractEndpoint):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.BulkCharacterNamesToLastShip = self.cm.BulkCharacterNamesToLastShip

    @staticmethod
    def default_ttl() -> int:
        return 30

    @staticmethod
    def _get_unprefixed_key_hash_sync(char_names: frozenset, seconds_ago_threshold: int):
        return "{}:{}".format(seconds_ago_threshold, hash(char_names))

    async def get(self, char_names: list, seconds_ago_threshold: int = 30) -> dict:
        set_char_names = await self.executor_thread(self.make_frozen_set, list_items=char_names)
        return await super().get(char_names=set_char_names, seconds_ago_threshold=seconds_ago_threshold)

    async def _do_endpoint_logic(self, char_names: frozenset, seconds_ago_threshold: int) -> dict:
        d = await self.BulkCharacterNamesToLastShip.get(char_names=char_names)
        return await self.executor_proc(self._do_endpoint_logic_sync, char_names=char_names, data_dict=d,
                                       seconds_ago_threshold=seconds_ago_threshold)

    @classmethod
    def _do_endpoint_logic_sync(cls, data_dict: dict, char_names: frozenset, seconds_ago_threshold: int):
        bucket_alliance = {}
        bucket_corp = {}
        all_items = []
        known_ships = Helpers.get_nested_value(data_dict, [], "data", "known")
        for e in known_ships:
            seconds_ago = (datetime.utcnow() - dateTimeParser(Helpers.get_nested_value(e, datetime.utcnow(), "time"))).total_seconds()
            if seconds_ago > seconds_ago_threshold:
                if (not Helpers.get_nested_value(e, False, "isSuperTitan")
                        and not Helpers.get_nested_value(e, False, "isRegularCap")):
                    ship_name = "UNKNOWN"
                else:
                    ship_name = Helpers.get_nested_value(e, "UNKNOWN", "ship", "type_name")
            else:
                ship_name = Helpers.get_nested_value(e, "UNKNOWN", "ship", "type_name")
            is_attacker = Helpers.get_nested_value(e, False, "attacker")
            system_data = Helpers.get_nested_value(e, {}, "system")
            location_data = Helpers.get_nested_value(e, {}, "location")
            km_data = Helpers.get_nested_value(e, {}, "km", "package", "killmail")
            corp_name = Helpers.get_nested_value(e, None, "corporation", "corporation_name")
            alliance_name = Helpers.get_nested_value(e, None, "alliance", "alliance_name")
            if alliance_name:
                alliance_bucket = bucket_alliance.setdefault(alliance_name, BucketManagerEntity(alliance_name))
                alliance_bucket.add_ship(ship_name, seconds_ago, system_data, location_data, km_data, is_attacker)
            elif corp_name:
                corp_bucket = bucket_corp.setdefault(corp_name, BucketManagerEntity(corp_name))
                corp_bucket.add_ship(ship_name, seconds_ago, system_data, location_data, km_data, is_attacker)
            else:
                pass
            all_d = {
                "character": Helpers.get_nested_value(e, None, "character"),
                "corporation": Helpers.get_nested_value(e, None, "corporation"),
                "alliance": Helpers.get_nested_value(e, None, "alliance"),
                "shipName": ship_name,
                "attacker": is_attacker,
                "seconds": seconds_ago,
                "system": system_data,
                "location": location_data
            }
            all_items.append(all_d)
        alliances_buckets_sorted = [v.to_dict() for v in bucket_alliance.values()]
        corporation_buckets_sorted = [v.to_dict() for v in bucket_corp.values()]
        return_dict = {
            "alliances": alliances_buckets_sorted,
            "corporations": corporation_buckets_sorted,
            "all": all_items,
            "queriedNames": list(char_names),
            "totalQueried": len(char_names),
            "totalUnknownNames": len(char_names) - len(known_ships)
        }
        return return_dict