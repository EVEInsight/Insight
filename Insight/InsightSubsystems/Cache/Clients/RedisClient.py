from InsightSubsystems.Cache.Clients.AbstractBaseClient import AbstractBaseClient
import aioredis
import time
import traceback
import InsightExc


class RedisClient(AbstractBaseClient):
    def __init__(self, config_class, thread_pool):
        super().__init__(config_class, thread_pool)
        self.host = self.config.get("REDIS_HOST")
        self.password = self.config.get("REDIS_PASSWORD")
        self.port = self.config.get("REDIS_PORT")
        self.db = self.config.get("REDIS_DB")
        self.client: aioredis.Redis = None

    async def establish_connection(self):
        if self.host == "":
            print("No Redis host is defined. Functions requiring Redis will not function until a valid instance is "
                  "provided.")
            return False
        try:
            self.client = await aioredis.create_redis_pool("redis://:{}@{}:{}/{}".
                                                           format(self.password, self.host, self.port, self.db),
                                                           timeout=5, encoding="utf-8")
            test_ok = await self.test_connection()
            if test_ok:
                return True
            else:
                return False
        except Exception as ex:
            traceback.print_exc()
            print("Error when attempting to establish a connection to the Redis host: redis://{}:{}. Insight will"
                  "operate without Redis and all functions that require Redis will not work.".format(self.host,
                                                                                                     self.port))
            return False

    async def test_connection(self):
        current_time = {"time": time.time()}
        await self.client.set("test_time", await self.serialize(current_time),expire=5)
        cache_time = await self.deserialize(await self.client.get("test_time"))
        if current_time != cache_time:
            return False
        else:
            return True

    async def get(self, key_str: str) -> dict:
        result = await self.client.get(key=key_str)
        if result is None:
            raise InsightExc.Subsystem.KeyDoesNotExist
        else:
            return await self.deserialize(result)

    async def set(self, key_str: str, ttl: int, data_dict: dict):
        await self.client.set(key=key_str, expire=ttl, value=await self.serialize(data_dict))
