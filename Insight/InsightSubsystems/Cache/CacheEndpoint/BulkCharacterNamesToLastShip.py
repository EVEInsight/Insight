from InsightSubsystems.Cache.CacheEndpoint.AbstractNoCacheEndpoint import AbstractNoCacheEndpoint
from InsightUtilities.StaticHelpers import *


class BulkCharacterNamesToLastShip(AbstractNoCacheEndpoint):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.BulkCharacterNameToID = self.cm.BulkCharacterNameToID
        self.BulkCharacterIDsToLastShip = self.cm.BulkCharacterIDsToLastShip

    @staticmethod
    def _get_unprefixed_key_hash_sync(char_names: frozenset):
        return "{}".format(hash(char_names))

    async def get(self, char_names: list) -> dict:
        set_char_names = await self.executor(self.make_frozen_set, list_items=char_names)
        return await super().get(char_names=set_char_names)

    @classmethod
    def _sort_known_characters_by_name(cls, known_ships: list):
        return sorted(known_ships, key=lambda x: x["character"]["character_name"].lower())

    async def _do_endpoint_logic(self, char_names: frozenset) -> dict:
        char_ids_resolved = await self.BulkCharacterNameToID.get(char_names=char_names)
        valid_char_ids_packed = await Helpers.async_get_nested_value(char_ids_resolved, [], "data", "characters")
        valid_char_ids = [await Helpers.async_get_nested_value(i, None, "id") for i in valid_char_ids_packed]
        bulk_ships_d = await self.BulkCharacterIDsToLastShip.get(char_ids=valid_char_ids)
        known = await Helpers.async_get_nested_value(bulk_ships_d, [], "data", "known")
        unknown_char_names: set = await self.executor(self.frozenset_to_set, char_names)
        for k in known:
            known_char_name = await Helpers.async_get_nested_value(k, "", "character", "character_name")
            unknown_char_names.remove(known_char_name)
        return_dict = {
            "data": {
                "known": await self.executor(self._sort_known_characters_by_name, known),
                "unknownNames": list(unknown_char_names),
                "totalQuery": len(char_names),
                "totalKnown": len(known),
                "totalUnknownNames": len(unknown_char_names)
            }
        }
        self.set_min_ttl(return_dict, await Helpers.async_get_nested_value(bulk_ships_d, self.default_ttl(), "redis", "ttl"))
        return return_dict


