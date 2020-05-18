from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
import asyncio
from InsightUtilities.StaticHelpers import *


class BulkCharacterNameToID(AbstractEndpoint):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.CharacterNameToId = self.cm.CharacterNameToID

    @staticmethod
    def default_ttl() -> int:
        return 7200  # 2 hours

    @staticmethod
    def _get_unprefixed_key_hash_sync(char_names: frozenset):
        return "{}".format(hash(char_names))

    async def get(self, char_names: list) -> dict:
        if isinstance(char_names, list):
            set_char_names = await self.executor_thread(self.make_frozen_set, char_names=char_names)
        elif isinstance(char_names, frozenset):
            set_char_names = char_names
        else:
            raise TypeError
        return await super().get(char_names=set_char_names)

    async def _do_endpoint_logic(self, char_names: frozenset) -> dict:
        awaitables = [self.CharacterNameToId.get(c) for c in char_names]
        results = []
        for f in asyncio.as_completed(awaitables, timeout=15):
            results.append(await f)
        return await self.executor_thread(self.make_return_dict, results)

    @classmethod
    def make_return_dict(cls, char_data: list) -> dict:
        return_dict = {
            "data": {
                "characters": [],
                "unknown": [],
                "total_query": len(char_data),
                "total_found": 0,
                "total_unknown": 0
            }
        }
        for d in char_data:
            found = Helpers.get_nested_value(d, False, "data", "found")
            if found:
                return_dict["data"]["characters"].append(Helpers.get_nested_value(d, False, "data"))
                return_dict["data"]["total_found"] += 1
            else:
                return_dict["data"]["unknown"].append(Helpers.get_nested_value(d, False, "data"))
                return_dict["data"]["total_unknown"] += 1
        cls.set_min_ttl(return_dict, cls.extract_min_ttl(*char_data))
        return return_dict
