from InsightUtilities import InsightSingleton, AsyncLockManager, DBSessions
from InsightSubsystems.Cache import CacheManager
import InsightExc
import asyncio
from functools import partial
import InsightLogger
from InsightUtilities.StaticHelpers import *


class AbstractEndpoint(metaclass=InsightSingleton):
    def __init__(self, cache_manager):
        self.cm: CacheManager.CacheManager = cache_manager
        self.key_prefix = str(str(self.__class__.__name__).replace("_", ""))
        self.lg = InsightLogger.InsightLogger.get_logger('Cache.{}'.format(self.key_prefix), 'Cache.log', child=True)
        self.lock = asyncio.Lock(loop=self.cm.loop)
        self.lock_key_strings = asyncio.Lock(loop=self.cm.loop)
        self.key_strings = {}
        self.ttl = self.default_ttl()
        self.key_locks = AsyncLockManager(self.cm.loop)
        self.loop = self.cm.loop
        self.thread_pool = self.cm.tp
        self.db_sessions: DBSessions = DBSessions()

    async def run_executor(self, callback, **kwargs):
        return await self.loop.run_in_executor(self.thread_pool, partial(callback, **kwargs))

    def _get_unprefixed_key_hash_sync(self, **kwargs) -> str:
        raise NotImplementedError

    async def _get_unprefixed_key_hash(self, **kwargs) -> str:
        return await self.loop.run_in_executor(self.thread_pool, partial(self._get_unprefixed_key_hash_sync, **kwargs))

    async def _get_prefixed_key(self, unprefixed_key: str) -> str:
        if unprefixed_key is None:
            return self.key_prefix
        else:
            async with self.lock_key_strings:
                k = self.key_strings.get(unprefixed_key)
                if k is None:
                    new_k = "{}:{}".format(self.key_prefix, unprefixed_key)
                    self.key_strings[unprefixed_key] = new_k
                    return new_k
                else:
                    return k

    async def _set(self, key_str: str, data_object: dict) -> dict:
        ttl = Helpers.get_nested_value(data_object, self.default_ttl(), "redis", "ttl")
        data_object.pop("redis", None)
        return await self.cm.set_and_get_cache(key_str, ttl, data_dict=data_object)

    async def get(self, **kwargs) -> dict:
        try:
            cache_key = await self._get_prefixed_key(await self._get_unprefixed_key_hash(**kwargs))
            async with (await self.key_locks.get_object(cache_key)):
                try:
                    return await self.cm.get_cache(cache_key)
                except InsightExc.Subsystem.KeyDoesNotExist:
                    st = InsightLogger.InsightLogger.time_start()
                    result = await self._do_endpoint_logic(**kwargs)
                    InsightLogger.InsightLogger.time_log(self.lg, st, 'logic - key: "{}"'.format(cache_key),
                                                         warn_higher=5000, seconds=False)
                    return await self._set(cache_key, result)
        except Exception as ex:
            self.lg.exception(ex)
            raise ex

    async def _do_endpoint_logic(self, **kwargs) -> dict:
        return await self.loop.run_in_executor(self.thread_pool, partial(self._do_endpoint_logic_sync, **kwargs))

    def _do_endpoint_logic_sync(self, **kwargs) -> dict:
        raise NotImplementedError

    def default_ttl(self) -> int:
        return 3600

    def extract_min_ttl(self, *args):
        min_ttl = self.default_ttl()
        for d in args:
            ttl = Helpers.get_nested_value(d, 0, "redis", "ttl")
            if ttl < min_ttl:
                min_ttl = ttl
        if min_ttl <= 0:
            min_ttl = 1
        return min_ttl

    def set_min_ttl(self, d: dict, ttl: int):
        if "redis" in d:
            d["redis"]["ttl"] = ttl
        else:
            d["redis"] = {
                "ttl": ttl
            }
