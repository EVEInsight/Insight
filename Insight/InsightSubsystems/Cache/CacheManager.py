from InsightSubsystems.SubsystemBase import SubsystemBase
from InsightSubsystems.Cache.Clients import RedisClient, NoRedisClient
from InsightSubsystems.Cache import CacheEndpoint
import sys
from concurrent.futures import ThreadPoolExecutor


class CacheManager(SubsystemBase):
    def __init__(self, subsystemloader):
        super().__init__(subsystemloader)
        self.tp = ThreadPoolExecutor(max_workers=5)
        self.client = NoRedisClient.NoRedisClient(self.config, self.tp)
        # self.TopKMs = CacheEndpoint.TopKMs(cache_manager=self)
        # self.TopKMsEmbed = CacheEndpoint.TopKMsEmbed(cache_manager=self)

    async def start_subsystem(self):
        try:
            redis = RedisClient.RedisClient(self.config, self.tp)
            if await redis.establish_connection():
                self.client = redis
                print("Redis connection established.")
            else:
                sys.stderr.write("Insight is operating without Redis. Please connect Insight to Redis for all functions"
                                 " to properly work.")
        except Exception as ex:
            print(ex)

    async def stop_subsystem(self):
        self.client.tp.shutdown(wait=True)

    async def get_cache(self, key_str: str) -> dict:
        return await self.client.get(key_str)

    async def set_cache(self, key_str: str, ttl: int, data_dict: dict):
        await self.client.set(key_str, ttl, data_dict)
