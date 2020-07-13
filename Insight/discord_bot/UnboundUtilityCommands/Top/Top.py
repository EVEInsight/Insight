from ..UnboundCommandBase import *
import discord
from InsightSubsystems.Cache.CacheEndpoint import MostExpensiveKMsEmbed


class Top(UnboundCommandBase):
    def __init__(self, unbound_service, is_main_command=False):
        super().__init__(unbound_service, is_main_command)
        self.mostexpensive = MostExpensiveKMsEmbed()

    def yield_subcommands(self):
        yield ["year", "y"], self.unbound.top_year.run_command
        yield ["month", "m"], self.unbound.top_month.run_command
        yield ["week", "w"], self.unbound.top_week.run_command
        yield ["day", "d"], self.unbound.top_day.run_command
        yield ["hour", "1h"], self.unbound.top_hour.run_command
        yield ["help", "h"], self.unbound.top_help.run_command

    @classmethod
    def mention(cls):
        return False

    async def get_top_embed(self, hour_range, d_message):
        prefix = await self.serverManager.get_min_prefix(d_message.channel)
        return await self.mostexpensive.get(last_hours=hour_range, server_prefix=prefix)

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        return await self.unbound.top_week.get_embed(d_message=d_message, message_text=message_text, **kwargs)

