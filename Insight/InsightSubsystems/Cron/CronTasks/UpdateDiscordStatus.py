from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask
import psutil
import discord
import InsightLogger


class UpdateDiscordStatus(AbstractCronTask):
    def __init__(self, cron_manager):
        super().__init__(cron_manager)
        self.lg_status = InsightLogger.InsightLogger.get_logger('Insight.status', 'Insight_status.log')
        self.status = discord.Status.dnd

    def loop_iteration(self) -> int:
        return 300

    def run_at_intervals(self) -> bool:
        return True

    def interval_offset(self) -> int:
        return 0

    def call_now(self) -> bool:
        return True

    def current_status(self):
        return self.status

    async def _run_task(self):
        update = await self.loop.run_in_executor(None, self.service.update_available)
        if update:
            status_str = 'Update available. See console. '
        else:
            status_str = ""
            if self.service.config.get("INSIGHT_STATUS_CPUMEM"):
                status_str += "CPU:{}% MEM:{:.1f}GB ".format(str(int(psutil.cpu_percent())),
                                                             psutil.virtual_memory()[3] / 2. ** 30)
            if self.service.config.get("INSIGHT_STATUS_VERSION_FEEDCOUNT"):
                status_str += "{} Feeds: {} ".format(str(self.service.get_version()),
                                                     self.channel_manager.feed_count())
        stats_zk = await self.loop.run_in_executor(None, self.zk.get_stats)
        d_status = discord.Status.online
        if self.service.config.get("INSIGHT_STATUS_TIME"):
            if stats_zk[0] <= 10:
                d_status = discord.Status.idle
            status_str += '[Stats 5m] [zK] Add: {}, Delay: {}m(+{}s) '.format(stats_zk[0], stats_zk[1], stats_zk[2])
            stats_feeds = await self.client.channel_manager.avg_delay()
            if stats_feeds[1] >= 25:
                d_status = discord.Status.dnd
            status_str += '[Insight] Sent: {}, Delay: {}s '.format(str(stats_feeds[0]),
                                                                   str(stats_feeds[1]))
        game_act = discord.Activity(name=status_str, type=discord.ActivityType.watching)
        await self.client.change_presence(activity=game_act, status=d_status)
        self.status = d_status
        self.lg_status.info(status_str)
