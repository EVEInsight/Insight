from InsightSubsystems.Cache.Clients.AbstractBaseClient import AbstractBaseClient


class NoRedisClient(AbstractBaseClient):
    def __init__(self, config_class, concurrent_pool):
        super().__init__(config_class, concurrent_pool)