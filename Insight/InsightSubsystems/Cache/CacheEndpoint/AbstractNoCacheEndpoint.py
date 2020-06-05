from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
import asyncio


class AbstractNoCacheEndpoint(AbstractEndpoint):
    async def get_lock(self, key_str: str):
        return asyncio.Lock()

    @staticmethod
    def default_ttl() -> int:
        return -1

    async def _set(self, key_str: str, data_object: dict) -> dict:
        data_object["redis"] = {
            "queryms": 0,
            "cacheHit": False,
            "usesCache": False
        }
        return data_object