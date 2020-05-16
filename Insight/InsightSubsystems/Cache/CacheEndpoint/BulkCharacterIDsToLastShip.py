from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
import asyncio
from InsightUtilities.StaticHelpers import *


class BulkCharacterIDsToLastShip(AbstractEndpoint):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.LastShip = self.cm.LastShip

    @staticmethod
    def default_ttl() -> int:
        return 30

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
        awaitables_last_ship = [self.LastShip.get(c) for c in char_ids]
        known_ship_data = []
        unknown_ids = []
        redis_ttls = []
        for f in asyncio.as_completed(awaitables_last_ship, timeout=5):
            last_ship_d = await f
            if not await Helpers.async_get_nested_value(last_ship_d, True, self.pool, "data", "known"):
                unknown_ids.append(await Helpers.async_get_nested_value(last_ship_d,
                                                                              -1, self.pool, "data", "queryID"))
            else:
                known_ship_data.append(await Helpers.async_get_nested_value(last_ship_d, {}, self.pool,
                                                                            "data"))
            redis_ttls.append({"redis": await Helpers.async_get_nested_value(last_ship_d, {}, self.pool, "redis")})
        return_dict = {
            "data": {
                "known": known_ship_data,
                "unknownIDs": unknown_ids,
                "totalQuery": len(char_ids),
                "totalKnown": len(known_ship_data),
                "totalUnknownIDs": len(unknown_ids),
            }
        }
        min_ttl = await self.executor_thread(self.extract_min_ttl, *redis_ttls)
        self.set_min_ttl(return_dict, min_ttl)
        return return_dict
