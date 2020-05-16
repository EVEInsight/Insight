from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
from InsightUtilities.StaticHelpers import *
from datetime import datetime
from dateutil.parser import parse as dateTimeParser
from operator import itemgetter
from InsightSubsystems.Cache.CacheEndpoint.EndpointUtils.TrackingBucket import TrackingBucket, TrackingBucketDual
from InsightSubsystems.Cache.CacheEndpoint.EndpointUtils.TrackingBucketEntity import TrackingBucketEntity
from collections import OrderedDict


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
        known_ships = Helpers.get_nested_value(data_dict, [], "data", "known")
        bucket_alliance = {}
        bucket_corp = {}
        bucket_ships = TrackingBucketDual("shipID", "ship", "characters", value_as_list=True)
        bucket_systems = TrackingBucketDual("systemID", "system", "characters", value_as_list=True)
        bucket_locations = TrackingBucketDual("locationID", "location", "characters", value_as_list=True)
        bucket_mails = TrackingBucketDual("kmID", "km", "characters", value_as_list=True)
        all_characters = {}
        for e in known_ships:
            is_unknown = False
            seconds_ago = (datetime.utcnow() - dateTimeParser(Helpers.get_nested_value(e, datetime.utcnow(), "time"))).total_seconds()
            if seconds_ago > seconds_ago_threshold:
                if (not Helpers.get_nested_value(e, False, "isSuperTitan")
                        and not Helpers.get_nested_value(e, False, "isRegularCap")):
                    is_unknown = True
            if not Helpers.get_nested_value(e, None, "ship", "type_name"):
                is_unknown = True
            is_attacker = Helpers.get_nested_value(e, False, "attacker")
            char_id = Helpers.get_nested_value(e, None, "character", "character_id")
            ship_data = Helpers.get_nested_value(e, {}, "ship")
            ship_id = Helpers.get_nested_value(ship_data, 0, "type_id")
            system_data = Helpers.get_nested_value(e, {}, "system")
            system_id = Helpers.get_nested_value(system_data, 0, "system_id")
            location_data = Helpers.get_nested_value(e, {}, "location")
            location_id = Helpers.get_nested_value(location_data, 0, "location_id")
            km_data = Helpers.get_nested_value(e, {}, "km", "package", "killmail")
            km_id = Helpers.get_nested_value(km_data, 0, "killmail_id")
            corp_data = Helpers.get_nested_value(e, None, "corporation")
            corp_id = Helpers.get_nested_value(corp_data, 0, "corporation_id")
            corp_name = Helpers.get_nested_value(corp_data, None, "corporation_name")
            alliance_data = Helpers.get_nested_value(e, None, "alliance")
            alliance_id = Helpers.get_nested_value(alliance_data, 0, "alliance_id")
            alliance_name = Helpers.get_nested_value(alliance_data, None, "alliance_name")
            if alliance_id:
                alliance_bucket = bucket_alliance.setdefault(
                    alliance_id, TrackingBucketEntity(alliance_id, alliance_name, True, alliance_data))
                alliance_bucket.add_ship(seconds_ago, ship_id, char_id, system_id, location_id,
                                         km_id, is_attacker, is_unknown)
            elif corp_id:
                corp_bucket = bucket_corp.setdefault(
                    corp_id, TrackingBucketEntity(corp_id, corp_name, False, corp_data))
                corp_bucket.add_ship(seconds_ago, ship_id, char_id, system_id, location_id,
                                     km_id, is_attacker, is_unknown)
            else:
                pass
            if char_id:
                bucket_mails.add_item(km_id, km_data, char_id)
                bucket_systems.add_item(system_id, system_data, char_id)
                bucket_locations.add_item(location_id, location_data, char_id)
                if is_unknown:
                    bucket_ships.add_item(None, None, char_id)
                else:
                    bucket_ships.add_item(ship_id, ship_data, char_id)
                all_d = {
                    "characterID": char_id,
                    "corporationID": corp_id,
                    "allianceID": alliance_id,
                    "shipID": ship_id,
                    "attacker": is_attacker,
                    "unknown": is_unknown,
                    "seconds": seconds_ago,
                    "systemID": system_id,
                    "locationID": location_id
                }
                all_characters[char_id] = all_d
        alliances_buckets_sorted = sorted([v.to_dict() for v in bucket_alliance.values()], key=itemgetter("total"), reverse=True)
        corporation_buckets_sorted = sorted([v.to_dict() for v in bucket_corp.values()], key=itemgetter("total"), reverse=True)
        ordered_alliances = OrderedDict((d["id"], d) for d in alliances_buckets_sorted)
        ordered_corps = OrderedDict((d["id"], d) for d in corporation_buckets_sorted)
        return_dict = {
            "alliances": ordered_alliances,
            "corporations": ordered_corps,
            "characters": all_characters,
            "shipHighestRatio": bucket_ships.get_top_dict(),
            "ships": bucket_ships.get_sorted_dict(),
            "systemHighestRatio": bucket_systems.get_top_dict(),
            "systems": bucket_systems.get_sorted_dict(),
            "locationHighestRatio": bucket_locations.get_top_dict(),
            "locations": bucket_locations.get_sorted_dict(),
            "kmHighestRatio": bucket_mails.get_top_dict(),
            "kms": bucket_mails.get_sorted_dict(),
            "queriedNames": list(char_names),
            "totalQueried": len(char_names),
            "totalUnknownNames": len(char_names) - len(known_ships)
        }
        return return_dict
