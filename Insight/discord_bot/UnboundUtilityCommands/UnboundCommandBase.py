from . import UnboundUtilityCommands
import discord
import random
import traceback
import datetime
import asyncio
from discord_bot import discord_options as dOpt
import InsightExc
from InsightUtilities import DiscordPermissionCheck

class UnboundCommandBase(object):
    def __init__(self, unbound_service):
        self.unbound: UnboundUtilityCommands = unbound_service
        self.client = self.unbound.client
        self.service = self.client.service
        self.embed_only = False

    def command_description(self):
        return "Not implemented."

    async def set_status(self, message_str: str):
        try:
            game_act = discord.Activity(name=message_str, type=discord.ActivityType.watching)
            await self.client.change_presence(activity=game_act, status=discord.Status.dnd)
        except Exception as ex:
            print(ex)

    async def send_status_message(self, d_message: discord.Message, message_str: str):
        try:
            print(message_str)
            await d_message.channel.send('{}\n{}'.format(d_message.author.mention, message_str))
        except Exception as ex:
            print(ex)

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs)->discord.Embed:
        e = discord.Embed()
        e.color = discord.Color(659493)
        e.timestamp = datetime.datetime.utcnow()
        e.set_author(name=self.__class__.__name__)
        e.set_footer(text='Utility command')
        e.description = await self.get_text(d_message, message_text, **kwargs)
        return e

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs)->str:
        return "Not implemented."

    def can_text(self, d_message: discord.Message):
        return DiscordPermissionCheck.can_text(d_message)

    def can_embed(self, d_message: discord.Message):
        can_embed = DiscordPermissionCheck.can_embed(d_message)
        if self.embed_only and not can_embed:
            raise InsightExc.DiscordError.DiscordPermissions("Insight is lacking the **embed links** and **send "
                                                             "messages** roles in this channel. You must enable "
                                                             "these roles to use this command.")
        return can_embed

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        if self.can_embed(d_message):
            await d_message.channel.send(content='{}\n'.format(d_message.author.mention), embed=await self.get_embed(d_message, m_text))
        elif self.can_text(d_message):
            response_text = "{}\n{}".format(d_message.author.mention, await self.get_text(d_message, m_text))
            if len(response_text) > 2000:
                response_text = response_text[:1850] + "\n!!Truncated - Enable embed links to get remainder of " \
                                                       "message through Discord rich embeds!!"
            await d_message.channel.send(content=response_text)
        else:  # permissions error
            return

