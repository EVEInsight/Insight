from ..UnboundCommandBase import *
from InsightSubsystems.Cache.CacheManager import CacheManager


class ResetCache(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.cLock = asyncio.Lock(loop=self.client.loop)

    def command_description(self):
        return "Purge Redis Cache - Delete all keys in the Redis cache."

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        async with self.cLock:
            options = dOpt.mapper_return_yes_no(self.client, d_message)
            options.set_main_header("Are you sure you want purge and empty the Redis cache?\n"
                                    "This operation will delete all keys in the Redis database.")
            resp = await options()
            if resp:
                await CacheManager().client.redis_purge_all_keys()
