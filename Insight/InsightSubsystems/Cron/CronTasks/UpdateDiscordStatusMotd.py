from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask
from InsightSubsystems.Cron.CronTasks.UpdateDiscordStatus import UpdateDiscordStatus
import discord
from InsightSubsystems.Cache.CacheEndpoint import InsightMeta
from InsightUtilities.StaticHelpers import Helpers
from datetime import datetime, timedelta


class UpdateDiscordStatusMotd(AbstractCronTask):
    def __init__(self, cron_manager):
        super().__init__(cron_manager)
        self.InsightMeta: InsightMeta = InsightMeta()
        self.DiscordStatus = UpdateDiscordStatus()

    def loop_iteration(self) -> int:
        return 300

    def run_at_intervals(self) -> bool:
        return True

    def interval_offset(self) -> int:
        return 150

    def call_now(self) -> bool:
        return False

    async def _run_task(self):
        motd = await self.InsightMeta.get("motd")
        last_modified = await Helpers.async_get_nested_value(motd, datetime.utcnow(), "data", "modified")
        if (datetime.utcnow() - timedelta(hours=24)) >= last_modified:
            return
        else:
            status_str = "MOTD has been updated. Run '!motd' to see the message of the day for " \
                         "announcements and updates. Status is cleared after 1 day."
            game_act = discord.Activity(name=status_str, type=discord.ActivityType.watching)
            await self.client.change_presence(activity=game_act, status=self.DiscordStatus.current_status())
