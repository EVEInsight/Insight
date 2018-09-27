from . import *
import discord
import discord_bot


class UnboundUtilityCommands(object):
    def __init__(self, insight_client):
        assert isinstance(insight_client, discord_bot.Discord_Insight_Client)
        self.client: discord_bot.Discord_Insight_Client = insight_client
        self.dscan = Dscan(self)
        self.eightBall = EightBall(self)

    def strip_command(self, message_object: discord.Message):
        try:
            return message_object.content.split(' ', 1)[1]
        except IndexError:
            return ''

    async def command_dscan(self, message_object: discord.Message):
        await self.dscan.command_dscan(message_object, self.strip_command(message_object))

    async def command_8ball(self, message_object: discord.Message):
        await self.eightBall.command_8ball(message_object, self.strip_command(message_object))
