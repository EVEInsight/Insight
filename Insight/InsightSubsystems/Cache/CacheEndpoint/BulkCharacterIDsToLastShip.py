from InsightSubsystems.Cache.CacheEndpoint.AbstractNoCacheEndpoint import AbstractNoCacheEndpoint
from InsightUtilities.StaticHelpers import *


class BulkCharacterIDsToLastShip(AbstractNoCacheEndpoint):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.LastShip = self.cm.LastShip

    @staticmethod
    def _get_unprefixed_key_hash_sync(char_ids: frozenset):
        return "{}".format(hash(char_ids))

    async def get(self, char_ids: list) -> dict:
        if isinstance(char_ids, list):
            set_char_ids = await self.executor_thread(self.make_frozen_set, list_items=char_ids)
        elif isinstance(char_ids, frozenset):
            set_char_ids = char_ids
        else:
            raise TypeError
        return await super().get(char_ids=set_char_ids)

    async def _do_endpoint_logic(self, char_ids: frozenset) -> dict:
        last_ships: dict = await self.LastShip.get(char_ids=char_ids)
        redis_times = []
        known_ship_data = []
        unknown_ids = []
        for char_id, last_ship_d in last_ships.items():
            if not await Helpers.async_get_nested_value(last_ship_d, True, self.pool, "data", "known"):
                unknown_ids.append(char_id)
            else:
                known_ship_data.append(await Helpers.async_get_nested_value(last_ship_d, {}, self.pool,
                                                                            "data"))
            redis_val = {"redis": await Helpers.async_get_nested_value(last_ship_d, {}, self.pool, "redis")}
            redis_times.append(redis_val)
        return_dict = {
            "data": {
                "known": known_ship_data,
                "unknownIDs": unknown_ids,
                "totalQuery": len(char_ids),
                "totalKnown": len(known_ship_data),
                "totalUnknownIDs": len(unknown_ids),
            }
        }
        min_ttl = await self.executor_thread(self.extract_min_ttl, *redis_times)
        self.set_min_ttl(return_dict, min_ttl)
        return return_dict
