from . import EightBall, Prefix, About, Help, Limits, Roll, Top, Motd
from .AdminCommands import Quit, Admin
from .LocalScan import LocalScan, LocalScanHelp, LocalScanAffiliations
from .Top import Top, TopHelp, TopHour, TopDay, TopWeek, TopMonth, TopYear
from .Time import Time, TimeWorld, TimeHelp
import discord
import discord_bot
from functools import partial
from typing import List


class UnboundUtilityCommands(object):
    def __init__(self, insight_client):
        assert isinstance(insight_client, discord_bot.Discord_Insight_Client)
        self.client: discord_bot.Discord_Insight_Client = insight_client
        self.serverManager = self.client.serverManager
        self.commandParser = self.client.commandLookup
        self.threadpool_unbound = self.client.threadpool_unbound
        self.localscan_affiliations = LocalScanAffiliations.LocalScanAffiliations(self)
        self.localscan_help = LocalScanHelp.LocalScanHelp(self)
        self.localscan = LocalScan.LocalScan(self, is_main_command=True)
        self.eightBall = EightBall.EightBall(self)
        self.prefix = Prefix.Prefix(self)
        self.about = About.About(self)
        self.help = Help.Help(self)
        self.quit = Quit.Quit(self)
        self.admin = Admin.Admin(self)
        self.limits = Limits.Limits(self)
        self.randomroll = Roll.Roll(self)
        self.top_year = TopYear.TopYear(self)
        self.top_month = TopMonth.TopMonth(self)
        self.top_week = TopWeek.TopWeek(self)
        self.top_day = TopDay.TopDay(self)
        self.top_hour = TopHour.TopHour(self)
        self.top_help = TopHelp.TopHelp(self)
        self.top = Top.Top(self, is_main_command=True)
        self.motd = Motd.Motd(self)
        self.time_world = TimeWorld.TimeWorld(self)
        self.time_help = TimeHelp.TimeHelp(self)
        self.time = Time.Time(self, is_main_command=True)

    async def strip_command(self, message_object: discord.Message):
        prefixes = await self.serverManager.get_server_prefixes(message_object.channel)
        return self.commandParser.strip_non_command(prefixes, message_object.content)

    def _do_split(self, input_str: str) -> list:
        return input_str.split()

    async def split_text(self, input_str: str) -> List[str]:
        return await self.client.loop.run_in_executor(None, partial(self._do_split, input_str))

    async def command_localscan(self, message_object: discord.Message):
        await self.localscan.run_command_proxy(message_object, await self.strip_command(message_object))

    async def command_8ball(self, message_object: discord.Message):
        await self.eightBall.run_command_proxy(message_object, await self.strip_command(message_object))

    async def command_quit(self, message_object: discord.Message):
        await self.quit.run_command_proxy(message_object, await self.strip_command(message_object))

    async def command_admin(self, message_object: discord.Message):
        await self.admin.run_command_proxy(message_object, await self.strip_command(message_object))

    async def command_prefix(self, message_object: discord.Message):
        await self.prefix.run_command_proxy(message_object, await self.strip_command(message_object))

    async def command_about(self, message_object: discord.Message):
        await self.about.run_command_proxy(message_object, await self.strip_command(message_object))

    async def command_help(self, message_object: discord.Message):
        await self.help.run_command_proxy(message_object, await self.strip_command(message_object))

    async def command_limits(self, message_object: discord.Message):
        await self.limits.run_command_proxy(message_object, await self.strip_command(message_object))

    async def command_roll(self, message_object: discord.Message):
        await self.randomroll.run_command_proxy(message_object, await self.strip_command(message_object))

    async def command_top(self, message_object: discord.Message):
        await self.top.run_command_proxy(message_object, await self.strip_command(message_object))

    async def command_motd(self, message_object: discord.Message):
        await self.motd.run_command_proxy(message_object, await self.strip_command(message_object))

    async def command_time(self, message_object: discord.Message):
        await self.time.run_command_proxy(message_object, await self.strip_command(message_object))
