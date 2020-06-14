from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
from InsightUtilities import MultiLock
import InsightLogger
import asyncio
import InsightExc
import copy


class AbstractMultiEndpoint(AbstractEndpoint):
    @staticmethod
    def _get_unprefixed_key_hash_sync(query_item, **kwargs) -> str:
        raise NotImplementedError

    async def set_dict_value(self, d: dict, data_result: dict, query_item, **kwargs):
        cache_key = await self._get_prefixed_key(await self._get_unprefixed_key_hash(query_item=query_item, **kwargs))
        d[query_item] = await self._set(cache_key, data_result)

    async def get(self, query_list: list, **kwargs) -> dict:
        st = InsightLogger.InsightLogger.time_start()
        try:
            if isinstance(query_list, set):
                query_set = await self.executor(copy.deepcopy, query_list)
            elif isinstance(query_list, list) or isinstance(query_list, frozenset):
                query_set: set = await self.executor(set, query_list)
            else:
                raise TypeError
            cache_hit = 0
            locks = []
            for item in query_set:
                cache_key = await self._get_prefixed_key(await self._get_unprefixed_key_hash(query_item=item,
                                                                                             **kwargs))
                lock = await self.get_lock(cache_key)
                locks.append(lock)
            multilock = MultiLock(locks)
            cached_dict = {}
            lookup_dict = {}
            cache_keys_to_query_item = {}
            async with multilock:
                awaitables = []
                for query_item in query_set:
                    cache_key = await self._get_prefixed_key(await self._get_unprefixed_key_hash(query_item=query_item,
                                                                                                 **kwargs))
                    cache_keys_to_query_item[cache_key] = query_item
                    awaitables.append(self.cm.get_cache_with_key(cache_key))
                for f in asyncio.as_completed(awaitables, timeout=15):
                    try:
                        key_queried, result = await f
                        query_item = cache_keys_to_query_item.get(key_queried)
                        cached_dict[query_item] = result
                        query_set.remove(query_item)
                        cache_hit += 1
                    except InsightExc.Subsystem.KeyDoesNotExist:
                        pass
                if len(query_set) > 0:
                    for q in query_set:
                        lookup_dict[q] = None
                    completed_lookup_dict = await self._do_endpoint_logic(lookup_dict, **kwargs)
                    awaitables_completed = []
                    for query_item, result in completed_lookup_dict.items():
                        awaitables_completed.append(self.set_dict_value(cached_dict, query_item=query_item,
                                                                        data_result=result))
                    for f in asyncio.as_completed(awaitables_completed, timeout=15):
                        await f
            InsightLogger.InsightLogger.time_log(self.lg, st, 'entirety - hit: {} - miss: {} queried keys: "{}"'.
                                                 format(cache_hit, len(query_set), query_set),
                                                 warn_higher=5000, seconds=False)
            return await self.process_before_return(cached_dict)
        except Exception as ex:
            self.lg.exception(ex)
            raise ex

    async def _do_endpoint_logic(self, lookup_dict: dict, **kwargs) -> dict:
        return await self.executor(self._do_endpoint_logic_sync, lookup_dict, **kwargs)

    def _do_endpoint_logic_sync(self, lookup_dict: dict, **kwargs) -> dict:
        raise NotImplementedError
