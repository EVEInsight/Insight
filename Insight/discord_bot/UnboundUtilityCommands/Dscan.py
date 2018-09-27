from . import *
import discord


class Dscan(object):
    def __init__(self, unbound_service):
        self.unbound: UnboundUtilityCommands = unbound_service
        self.resp = "The Dscan service is currently in development!"

    async def command_dscan(self, message_object: discord.Message, message_text: str):
        await message_object.channel.send('{}\n{}'.format(message_object.author.mention, self.resp))


