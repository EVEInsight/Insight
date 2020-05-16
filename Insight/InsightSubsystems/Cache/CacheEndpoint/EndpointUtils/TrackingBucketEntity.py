from InsightSubsystems.Cache.CacheEndpoint.EndpointUtils.TrackingBucket import TrackingBucket
from statistics import mean


class TrackingBucketEntity(object):
    def __init__(self, entity_id, name, is_alliance, entity_data):
        self.name = name
        self.id = entity_id
        self.is_alliance = is_alliance
        self.is_corporation = not is_alliance
        self.entity_data = entity_data
        self.ships = {}
        self.ship_delays = {}
        self.locations = TrackingBucket("organizationID", "locationID")
        self.systems = TrackingBucket("organizationID", "systemID")
        self.mails = TrackingBucket("organizationID", "kmID")
        self.characters = TrackingBucket("organizationID", "characters", value_as_list=True)
        self.total = 0
        self.alive = 0
        self.dead = 0

    def add_ship(self, seconds_ago: float, ship_id: int, character_id: int, system_id: int, location_id: int,
                 km_id: int, is_attacker: bool, is_unknown: bool):
        if is_unknown:
            ship_id = 0
        ship_counts = self.ships.setdefault(ship_id, {"shipID": ship_id, "alive": 0, "lost": 0, "total": 0, "avgSeconds": 0})
        ship_delays: list = self.ship_delays.setdefault(ship_id, [])
        ship_delays.append(seconds_ago)
        self.total += 1
        if is_attacker:
            ship_counts["alive"] += 1
            self.alive += 1
        else:
            if not is_unknown:
                ship_counts["lost"] += 1
                self.dead += 1
            else:
                ship_counts["alive"] += 1
                self.alive += 1
        ship_counts["total"] += 1
        if character_id:
            self.characters.add_item(self.id, character_id)
        if location_id:
            self.locations.add_item(self.id, location_id)
        if system_id:
            self.systems.add_item(self.id, system_id)
        if km_id and is_attacker:
            self.mails.add_item(self.id, km_id)

    def ships_calc_get_dict(self):
        for k, v in self.ships.items():
            avg_delay = mean(self.ship_delays[k]) if len(self.ship_delays[k]) else 0
            v["avgSeconds"] = avg_delay

    def get_sorted_list(self, count_tracking_dict):
        return sorted(count_tracking_dict.items(), key=lambda x: x[1]["total"], reverse=True)

    def to_dict(self) -> dict:
        return_dict = {
            "name": self.name,
            "id": self.id,
            "data": self.entity_data,
            "isAlliance": self.is_alliance,
            "isCorporation": self.is_corporation,
            "ships": self.ships_calc_get_dict(),
            "systemHighestRatio": self.systems.get_top_dict(),
            "systemCounts": self.systems.get_sorted_list(),
            "locationHighestRatio": self.locations.get_top_dict(),
            "locationCounts": self.locations.get_sorted_list(),
            "kmHighestRatio": self.mails.get_top_dict(),
            "kmCounts": self.mails.get_sorted_list(),
            "alive": self.alive,
            "dead": self.dead,
            "total": self.total
        }
        return return_dict
