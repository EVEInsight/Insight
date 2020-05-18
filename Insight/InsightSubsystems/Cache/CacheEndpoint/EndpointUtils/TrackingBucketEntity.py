from InsightSubsystems.Cache.CacheEndpoint.EndpointUtils.TrackingBucket import TrackingBucket, TrackingBucketDual
from statistics import mean
from collections import OrderedDict


class TrackingBucketEntity(object):
    def __init__(self, entity_id, name, is_alliance, entity_data):
        self.name = name
        self.id = entity_id
        self.is_alliance = is_alliance
        self.is_corporation = not is_alliance
        self.entity_data = entity_data
        self.ships = {}
        self.ship_delays = {}
        self.locations = TrackingBucket("locationID", "locationID")
        self.systems = TrackingBucket("systemID", "systemID")
        self.mails = TrackingBucket("kmID", "kmID")
        self.characters = OrderedDict()
        self.total = 0
        self.alive = 0
        self.unknown = 0
        self.dead = 0

    def add_ship(self, seconds_ago: float, ship_id: int, character_id: int, system_id: int, location_id: int,
                 km_id: int, is_attacker: bool, is_unknown: bool):
        if is_unknown:
            ship_id = 0
        ship_counts = self.ships.setdefault(ship_id, {"shipID": ship_id, "alive": 0, "dead": 0, "total": 0, "avgSeconds": 0})
        ship_delays: list = self.ship_delays.setdefault(ship_id, [])
        ship_delays.append(seconds_ago)
        if is_attacker:
            self.alive += 1
            ship_counts["alive"] += 1
            if is_unknown:
                self.unknown += 1
        else:
            self.dead += 1
            ship_counts["dead"] += 1
            if is_unknown:
                self.unknown += 1
        self.total += 1
        ship_counts["total"] += 1
        if character_id:
            self.characters[character_id] = {"characterID": character_id, "alive": is_attacker, "unknown": is_unknown}
        if location_id:
            self.locations.add_item(location_id, location_id)
            self.locations.append_item_unique(location_id, "characterIDs", character_id)
        if system_id:
            self.systems.add_item(system_id, system_id)
            self.systems.append_item_unique(system_id, "characterIDs", character_id)
            if location_id:
                self.systems.append_item_unique(system_id, "locationIDs", location_id)
        if km_id:
            self.mails.add_item(km_id, km_id)
            self.mails.append_item_unique(km_id, "characterIDs", character_id)

    def ships_calc_get_dict(self):
        for k, v in self.ships.items():
            avg_delay = mean(self.ship_delays[k]) if len(self.ship_delays[k]) else 0
            v["avgSeconds"] = avg_delay

    def get_sorted_list(self, count_tracking_dict, sort_key="total"):
        return sorted(count_tracking_dict.items(), key=lambda x: x[1][sort_key], reverse=True)

    def to_dict(self) -> dict:
        return_dict = {
            "name": self.name,
            "id": self.id,
            "data": self.entity_data,
            "isAlliance": self.is_alliance,
            "isCorporation": self.is_corporation,
            "characters": self.characters,
            "ships": self.ships_calc_get_dict(),
            "systemHighestRatio": self.systems.get_top_dict(),
            "systems": self.systems.get_sorted_dict(),
            "locationHighestRatio": self.locations.get_top_dict(),
            "locations": self.locations.get_sorted_dict(),
            "kmHighestRatio": self.mails.get_top_dict(),
            "kms": self.mails.get_sorted_dict(),
            "totalAlive": self.alive,
            "totalUnknown": self.unknown,
            "totalDead": self.dead,
            "total": self.total
        }
        return return_dict
