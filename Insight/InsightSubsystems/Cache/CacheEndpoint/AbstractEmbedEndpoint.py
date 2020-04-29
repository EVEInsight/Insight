from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
import discord
from discord.embeds import EmptyEmbed
from InsightUtilities.StaticHelpers import *
from datetime import datetime
from functools import partial


class AbstractEmbedEndpoint(AbstractEndpoint):
    def default_color(self) -> int:
        return 659493

    def make_embed(self, d: dict) -> discord.Embed:
        e = discord.Embed()
        e.color = Helpers.get_nested_value(d, 659493, "color")
        e.timestamp = datetime.utcfromtimestamp(Helpers.get_nested_value(d, datetime.utcnow(), "timestamp"))
        e.set_author(name=Helpers.get_nested_value(d, EmptyEmbed, "author", "name"),
                     url=Helpers.get_nested_value(d, EmptyEmbed, "author", "url"),
                     icon_url=Helpers.get_nested_value(d, EmptyEmbed, "author", "icon_url"))
        for f in Helpers.get_nested_value(d, [], "fields"):
            e.add_field(name=Helpers.get_nested_value(f, "-", "name"),
                        value=Helpers.get_nested_value(f, "-", "value"),
                        inline=Helpers.get_nested_value(f, "-", "inline"))
        image = Helpers.get_nested_value(d, None, "image")
        if image:
            e.set_image(url=image)
        desc = Helpers.get_nested_value(d, None, "description")
        if desc:
            e.description = desc
        thumbnail = Helpers.get_nested_value(d, None, "thumbnail")
        if thumbnail:
            e.set_thumbnail(url=thumbnail)
        e.set_footer(text=Helpers.get_nested_value(d, EmptyEmbed, "footer", "text"),
                     icon_url=Helpers.get_nested_value(d, EmptyEmbed, "footer", "icon_url"))
        return e

    async def get(self, **kwargs) -> discord.Embed:
        response = await super().get(**kwargs)
        return await self.loop.run_in_executor(self.thread_pool, partial(self.make_embed, response))
