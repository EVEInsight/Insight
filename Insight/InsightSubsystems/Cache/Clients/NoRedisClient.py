from InsightSubsystems.Cache.Clients.AbstractBaseClient import AbstractBaseClient


class NoRedisClient(AbstractBaseClient):
    def __init__(self, config_class, thread_pool):
        super().__init__(config_class, thread_pool)