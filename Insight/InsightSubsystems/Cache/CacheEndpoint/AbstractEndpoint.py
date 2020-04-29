from InsightUtilities import InsightSingleton, AsyncLockManager, DBSessions
from InsightSubsystems.Cache import CacheManager
import InsightExc
import asyncio
from functools import partial
import InsightLogger


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

    async def _set(self, key_str: str, ttl: int, data_object: dict):
        if ttl is None:
            ttl = self.ttl
        await self.cm.set_cache(key_str, ttl, data_dict=data_object)

    async def get(self, **kwargs) -> dict:
        try:
            cache_key = await self._get_prefixed_key(await self._get_unprefixed_key_hash(**kwargs))
            async with (await self.key_locks.get_object(cache_key)):
                try:
                    return await self.cm.get_cache(cache_key)
                except InsightExc.Subsystem.KeyDoesNotExist:
                    result = await self._do_endpoint_logic(**kwargs)
                    await self._set(cache_key, self.ttl, result)
                    return result
        except Exception as ex:
            self.lg.exception(ex)
            raise ex

    async def _do_endpoint_logic(self, **kwargs) -> dict:
        return await self.loop.run_in_executor(self.thread_pool, partial(self._do_endpoint_logic_sync, **kwargs))

    def _do_endpoint_logic_sync(self, **kwargs) -> dict:
        raise NotImplementedError

    def default_ttl(self) -> int:
        return 3600


