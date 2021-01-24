from ..UnboundCommandBase import *
import discord
from InsightUtilities.EmbedLimitedHelper import EmbedLimitedHelper
from dateutil import tz


class Time(UnboundCommandBase):
    def __init__(self, unbound_service, is_main_command=False):
        super().__init__(unbound_service, is_main_command)

    def yield_subcommands(self):
        yield ["help", "h"], self.unbound.time_help.run_command
        yield ["utc"], self.run_command
        yield ["world", "w"], self.unbound.time_world.run_command

    @classmethod
    def mention(cls):
        return False

    @classmethod
    def embed_only(cls):
        return False

    def time_utc(self):
        return datetime.datetime.utcnow()

    def time_local(self, iana_str):
        self.time_utc().astimezone(tz.gettz(iana_str))

    def format_time(self, datetime_object: datetime.datetime, formatter="%Y-%m-%d %H:%M"):
        return datetime_object.strftime(formatter)

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs) -> str:
        date_obj = self.time_utc()
        prefix = await self.serverManager.get_min_prefix(d_message.channel)
        s = "EVE Time (UTC)\n\n"
        s += "**Time:** {}\n".format(self.format_time(date_obj, "%H:%M:%S"))
        s += "**Date:** {}\n".format(self.format_time(date_obj, "%Y-%m-%d"))
        s += "**Day :** {}\n".format(self.format_time(date_obj, "%A"))
        s += "\nRun '{}time help' for additional command usage.".format(prefix)
        return s

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        prefix = await self.serverManager.get_min_prefix(d_message.channel)
        e = EmbedLimitedHelper()
        e.set_color(discord.Color(0x49b0b6))
        e.set_timestamp(datetime.datetime.utcnow())
        e.set_author(name="EVE Time (UTC)")
        date_obj = self.time_utc()
        e.add_field(name="Time:", value="{}".format(self.format_time(date_obj, "%H:%M:%S")), inline=True)
        e.add_field(name="Date:", value="{}".format(self.format_time(date_obj, "%Y-%m-%d")), inline=True)
        e.add_field(name="Day:", value="{}".format(self.format_time(date_obj, "%A")), inline=True)
        e.set_footer(text="Run '{}time help' for additional command usage.".format(prefix))
        return e

