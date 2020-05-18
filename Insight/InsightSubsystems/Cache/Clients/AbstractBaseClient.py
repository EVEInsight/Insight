from InsightUtilities import ConfigLoader
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from functools import partial
import InsightExc
import InsightLogger


class AbstractBaseClient(object):
    def __init__(self, config_class, concurrent_pool):
        self.lg = InsightLogger.InsightLogger.get_logger('Cache.Client', 'Cache.log', child=True)
        self.config: ConfigLoader = config_class
        self.loop = asyncio.get_event_loop()
        self.pool: ThreadPoolExecutor = concurrent_pool

    async def get(self, key_str: str) -> dict:
        raise InsightExc.Subsystem.NoRedis

    async def set(self, key_str: str, ttl: int, data_dict: dict):
        raise InsightExc.Subsystem.NoRedis

    async def delete(self, key_str: str):
        pass # no error on non redis client

    @staticmethod
    def _serialize(obj: dict):
        return json.dumps(obj)

    async def serialize(self, obj: dict) -> str:
        return await self.loop.run_in_executor(self.pool, partial(self._serialize, obj))

    @staticmethod
    def _deserialize(obj: str) -> dict:
        return json.loads(obj)

    async def deserialize(self, obj: str) -> dict:
        return await self.loop.run_in_executor(self.pool, partial(self._deserialize, obj))

    async def get_ttl(self, key_str: str) -> int:
        raise InsightExc.Subsystem.NoRedis

