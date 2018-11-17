from . import UnboundUtilityCommands
import discord
import random
import traceback
import datetime
import asyncio
from discord_bot import discord_options as dOpt


class UnboundCommandBase(object):
    def __init__(self, unbound_service):
        self.unbound: UnboundUtilityCommands = unbound_service
        self.client = self.unbound.client
        self.service = self.client.service

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

    def get_embed(self, message_text: str)->discord.Embed:
        e = discord.Embed()
        e.color = discord.Color(659493)
        e.timestamp = datetime.datetime.utcnow()
        e.set_author(name=self.__class__.__name__)
        e.set_footer(text='Utility command')
        e.description = self.get_text(message_text)
        return e

    def get_text(self, message_text: str)->str:
        return "Not implemented."

    @classmethod
    def can_text(cls, d_message: discord.Message):
        if isinstance(d_message.channel, discord.TextChannel):
            p: discord.Permissions = d_message.channel.permissions_for(d_message.channel.guild.me)
            return p.send_messages
        else:  # private convo so no need to check for permissions. Bot can embed
            return True

    @classmethod
    def can_embed(cls, d_message: discord.Message):
        if isinstance(d_message.channel, discord.TextChannel):
            p: discord.Permissions = d_message.channel.permissions_for(d_message.channel.guild.me)
            return p.embed_links and p.send_messages
        else:  # private convo so no need to check for permissions. Bot can embed
            return True

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        try:
            if self.can_embed(d_message):
                await d_message.channel.send(content='{}\n'.format(d_message.author.mention), embed=self.get_embed(m_text))
            elif self.can_text(d_message):
                await d_message.channel.send(content='{}\n{}'.format(d_message.author.mention, self.get_text(m_text)))
            else:  # permissions error
                pass
        except discord.HTTPException as ex:
            if 500 < ex.code < 600:
                pass
            else:
                print("Error when sending Discord unbound utility command response: {}".format(ex))
