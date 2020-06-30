from .LocalScan import LocalScan
import discord
import datetime


class LocalScanHelp(LocalScan):
    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs) ->str:
        return "Help command for local scan"  # todo

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) ->discord.Embed:
        e = discord.Embed()  # todo
        e.color = discord.Color(659493)
        e.timestamp = datetime.datetime.utcnow()
        e.set_author(name=self.__class__.__name__)
        e.set_footer(text='Utility command')
        e.description = await self.get_text(d_message, message_text, **kwargs)
        return e
