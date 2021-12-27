from InsightUtilities import InsightSingleton
import discord_bot
import service
import InsightLogger
from InsightSubsystems.Cache.CacheManager import CacheManager
from InsightSubsystems.Cron.CronManager import CronManager
from InsightSubsystems.WebAPI.WebAPI import WebAPI

class SubsystemLoader(metaclass=InsightSingleton):
    def __init__(self, discord_client):
        self.lg = InsightLogger.InsightLogger.get_logger('Subsystem.Loader', 'InsightUtilities.log', child=True)
        self.client: discord_bot.Discord_Insight_Client = discord_client
        self.service: service.ServiceModule = self.client.service
        self.insight_ready_event = self.client.insight_ready_event
        self.loop = self.client.loop
        self.subsystems = []
        self.subsystems.append(CacheManager(subsystemloader=self))
        self.subsystems.append(CronManager(subsystemloader=self))
        self.subsystems.append(WebAPI(subsystemloader=self))

    async def start_tasks(self):
        self.lg.info("Waiting for ready signal.")
        await self.insight_ready_event.wait()
        self.lg.info("Received ready signal... starting subsystem tasks.")
        for s in self.subsystems:
            self.loop.create_task(s.start_subsystem())

    async def stop_tasks(self):
        self.lg.info("Received shutdown signal... stopping subsystem tasks.")
        for s in self.subsystems:
            await s.stop_subsystem()
