from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
import asyncio
from InsightUtilities.StaticHelpers import *


class BulkCharacterIDsToLastShip(AbstractEndpoint):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.LastShip = self.cm.LastShip

    def default_ttl(self) -> int:
        return 30

    def make_frozen_set(self, char_ids: list):
        return frozenset(char_ids)

    def _get_unprefixed_key_hash_sync(self, char_ids: frozenset):
        return "{}".format(hash(char_ids))

    async def get(self, char_ids: list) -> dict:
        if isinstance(char_ids, list):
            set_char_ids = await self.run_executor(self.make_frozen_set, char_ids=char_ids)
        elif isinstance(char_ids, frozenset):
            set_char_ids = char_ids
        else:
            raise TypeError
        return await super().get(char_ids=set_char_ids)

    async def _do_endpoint_logic(self, char_ids: frozenset) -> dict:
        awaitables_last_ship = [self.LastShip.get(c) for c in char_ids]
        known_ship_data = []
        unknown_ship_data = []
        for f in asyncio.as_completed(awaitables_last_ship, timeout=5):
            last_ship_d = await f
            if not await Helpers.async_get_nested_value(last_ship_d, True, self.thread_pool, "data", "known"):
                unknown_ship_data.append(await Helpers.async_get_nested_value(last_ship_d,
                                                                              {}, self.thread_pool, "data"))
            else:
                known_ship_data.append(await Helpers.async_get_nested_value(last_ship_d, {}, self.thread_pool,
                                                                            "data"))
        return_dict = {
            "data": {
                "known": known_ship_data,
                "unknown": unknown_ship_data,
                "totalQuery": len(char_ids),
                "totalKnown": len(known_ship_data),
                "totalUnknown": len(unknown_ship_data),
            }
        }
        return return_dict
