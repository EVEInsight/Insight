from . import options_base
import discord

class Options_CapRadar(options_base.Options_Base):
    """InsightOption_  InsightOptionRequired_"""
    async def InsightOptionRequired_1(self, message_object:discord.Message):
        await message_object.channel.send("option1")