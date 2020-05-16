from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
import discord
from discord.embeds import EmptyEmbed
from InsightUtilities.StaticHelpers import *
from datetime import datetime
from functools import partial


class AbstractEmbedEndpoint(AbstractEndpoint):
    @staticmethod
    def default_ttl() -> int:
        return 30

    @staticmethod
    def default_color() -> discord.Color:
        return discord.Color(659493)

    def make_embed(self, d: dict) -> discord.Embed:
        discord_embed_dict = Helpers.get_nested_value(d, {}, "embed")
        e = discord.Embed.from_dict(discord_embed_dict)
        return e

    async def get(self, **kwargs) -> discord.Embed:
        response = await super().get(**kwargs)
        return await self.executor_thread(self.make_embed, response)
