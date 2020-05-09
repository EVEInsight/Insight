from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
import asyncio
from InsightUtilities.StaticHelpers import *
from InsightUtilities import EmbedLimitedHelper


class BulkCharacterNamesToLastShip(AbstractEndpoint):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.BulkCharacterNameToID = self.cm.BulkCharacterNameToID
        self.BulkCharacterIDsToLastShip = self.cm.BulkCharacterIDsToLastShip

    @staticmethod
    def default_ttl() -> int:
        return 30

    @staticmethod
    def _get_unprefixed_key_hash_sync(char_names: frozenset):
        return "{}".format(hash(char_names))

    async def get(self, char_names: list) -> dict:
        set_char_names = await self.executor_thread(self.make_frozen_set, list_items=char_names)
        return await super().get(char_names=set_char_names)

    async def _do_endpoint_logic(self, char_names: frozenset) -> dict:
        char_ids_resolved = await self.BulkCharacterNameToID.get(char_names=char_names)
        valid_char_ids_packed = await Helpers.async_get_nested_value(char_ids_resolved, [], self.pool,
                                                                     "data", "characters")
        valid_char_ids = [await Helpers.async_get_nested_value(i, None, self.pool, "id")
                          for i in valid_char_ids_packed]
        bulk_ships_d = await self.BulkCharacterIDsToLastShip.get(char_ids=valid_char_ids)
        known = await Helpers.async_get_nested_value(bulk_ships_d, [], self.pool, "data", "known")
        unknown_char_names: set = await self.executor_thread(self.frozenset_to_set, char_names)
        for k in known:
            known_char_name = await Helpers.async_get_nested_value(k, "", self.pool, "character",
                                                                   "character_name")
            unknown_char_names.remove(known_char_name)
        return_dict = {
            "data": {
                "known": known,
                "unknownNames": list(unknown_char_names),
                "totalQuery": len(char_names),
                "totalKnown": len(known),
                "totalUnknownNames": len(unknown_char_names)
            }
        }
        self.set_min_ttl(return_dict, await Helpers.async_get_nested_value(bulk_ships_d, self.default_ttl(),
                                                                           self.pool, "redis", "ttl"))
        return return_dict


