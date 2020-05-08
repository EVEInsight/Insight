from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
import asyncio
from InsightUtilities.StaticHelpers import *
from InsightUtilities import EmbedLimitedHelper


class BulkCharacterNamesToLastShip(AbstractEndpoint):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.BulkCharacterNameToID = self.cm.BulkCharacterNameToID
        self.BulkCharacterIDsToLastShip = self.cm.BulkCharacterIDsToLastShip

    def default_ttl(self) -> int:
        return 30

    def make_frozen_set(self, char_names: list):
        return frozenset(char_names)

    def _get_unprefixed_key_hash_sync(self, char_names: frozenset):
        return "{}".format(hash(char_names))

    async def get(self, char_names: list) -> dict:
        set_char_names = await self.run_executor(self.make_frozen_set, char_names=char_names)
        return await super().get(char_names=set_char_names)

    async def _do_endpoint_logic(self, char_names: frozenset) -> dict:
        char_ids_resolved = await self.BulkCharacterNameToID.get(char_names=char_names)
        valid_char_ids_packed = await Helpers.async_get_nested_value(char_ids_resolved, [], self.thread_pool,
                                                                     "data", "characters")
        valid_char_ids = [await Helpers.async_get_nested_value(i, None, self.thread_pool, "id")
                          for i in valid_char_ids_packed]
        unknown_names_packed = await Helpers.async_get_nested_value(char_ids_resolved, [], self.thread_pool, "data",
                                                                    "unknown")
        unknown_names = [await Helpers.async_get_nested_value(i, "", self.thread_pool, "name") for i in unknown_names_packed]
        bulk_ships_d = await self.BulkCharacterIDsToLastShip.get(char_ids=valid_char_ids)
        known = await Helpers.async_get_nested_value(bulk_ships_d, [], self.thread_pool, "data", "known")
        unknown = await Helpers.async_get_nested_value(bulk_ships_d, [], self.thread_pool, "data", "unknown")
        return_dict = {
            "data": {
                "known": known,
                "unknown": unknown,
                "unknownNames": unknown_names,
                "totalQuery": len(char_names),
                "totalKnown": len(known),
                "totalUnknown": len(unknown),
                "totalUnknownNames": len(unknown_names)
            }
        }
        self.set_min_ttl(return_dict, await Helpers.async_get_nested_value(bulk_ships_d, self.default_ttl(),
                                                                           self.thread_pool, "redis", "ttl"))
        return return_dict


