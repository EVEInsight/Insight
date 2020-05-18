from .UnboundCommandBase import *
import discord
from InsightSubsystems.Cache.CacheEndpoint import MostExpensiveKMsEmbed


class Top(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.mostexpensive = MostExpensiveKMsEmbed()

    @classmethod
    def mention(cls):
        return False

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        prefix = await self.serverManager.get_min_prefix(d_message.channel)
        embed = await self.mostexpensive.get(last_hours=168, server_prefix=prefix)
        return embed

