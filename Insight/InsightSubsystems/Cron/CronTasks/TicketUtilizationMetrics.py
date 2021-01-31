from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask
import InsightLogger
from InsightUtilities import LimitManager


class TicketUtilizationMetrics(AbstractCronTask):
    def __init__(self, cron_manager):
        super().__init__(cron_manager)
        self.lg_metric = InsightLogger.InsightLogger.get_logger('TicketUtilizationMetrics', 'TicketUtilizationMetrics.log')
        self.lm = LimitManager()
        self.metric_max = self.service.config.get("METRIC_LIMITER_MAX")

    def loop_iteration(self) -> int:
        return 300

    def run_at_intervals(self) -> bool:
        return True

    def interval_offset(self) -> int:
        return 0

    def call_now(self) -> bool:
        return False

    async def get_sorted_limiters(self):
        return []

    def str_metric(self):
        return ""

    def str_stats(self, pos, d):
        s = "{p:<5} {name:<50} {used_tickets:<10} {available:<12} {usage_ratio:<14} {pending:<8}\n".\
            format(p=pos, name=d.get("name"), used_tickets=d.get("used_tickets"), available=d.get("available"),
                   usage_ratio="{}%".format(d.get("usage_ratio")), pending=d.get("queue_length"))
        return s

    async def _run_task(self):
        s = "\n===== Ticket utilization report for {} over a period of {} seconds =====\n".format(self.str_metric(),
                                                                                                  self.loop_iteration())
        global_stats: dict = self.lm.get_server_sustained_limiter().stats(no_redact=True)
        s += "{:<20} {}\n".format("Global tickets consumed:", global_stats.get("used_tickets"))
        s += "{:<20} {}\n".format("Global tickets available:", global_stats.get("available"))
        s += "{:<20} {}\n".format("Global tickets pending:", global_stats.get("queue_length"))
        s += "{}\n".format("-" * 105)
        s += "{:<5} {:<50} {:<10} {:<12} {:<14} {:<8}\n".format("", "Name", "Consumed", "Remaining", "Usage Ratio",
                                                                 "Pending")
        current_index = 1
        for limiter in await self.get_sorted_limiters():
            s += self.str_stats(current_index, limiter.stats(no_redact=True))
            current_index += 1
            if current_index > self.metric_max:
                break
        s += "{}\n\n\n".format("=" * 105)
        self.lg_metric.info(s)


class TicketUtilizationMetrics_Servers(TicketUtilizationMetrics):
    def loop_iteration(self) -> int:
        return self.service.config.get("LIMITER_GUILD_SUSTAIN_INTERVAL")

    def interval_offset(self) -> int:
        return 0

    async def get_sorted_limiters(self):
        return await self.lm.sorted_servers_consumed()

    def str_metric(self):
        return "servers"


class TicketUtilizationMetrics_Channels(TicketUtilizationMetrics):
    def loop_iteration(self) -> int:
        return self.service.config.get("LIMITER_CHANNEL_SUSTAIN_INTERVAL")

    def interval_offset(self) -> int:
        return 10

    async def get_sorted_limiters(self):
        return await self.lm.sorted_channels_consumed()

    def str_metric(self):
        return "channels"


class TicketUtilizationMetrics_Users(TicketUtilizationMetrics):
    def loop_iteration(self) -> int:
        return self.service.config.get("LIMITER_USER_SUSTAIN_INTERVAL")

    def interval_offset(self) -> int:
        return 20

    async def get_sorted_limiters(self):
        return await self.lm.sorted_users_consumed()

    def str_metric(self):
        return "users"
