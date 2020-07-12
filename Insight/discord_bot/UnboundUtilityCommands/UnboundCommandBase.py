from . import UnboundUtilityCommands
import discord
import random
import traceback
import datetime
import asyncio
from discord_bot import discord_options as dOpt
import InsightExc
from InsightUtilities import DiscordPermissionCheck, LimitManager
import InsightUtilities
from functools import partial


class UnboundCommandBase(object):
    def __init__(self, unbound_service, is_main_command=False):
        self.unbound: UnboundUtilityCommands = unbound_service
        self.client = self.unbound.client
        self.service = self.client.service
        self.loop = self.client.loop
        self.serverManager = self.unbound.serverManager
        self.config = InsightUtilities.ConfigLoader()
        self.subcommands = {}
        if is_main_command:
            self.load_subcommands()

    def load_subcommands(self):
        prefix = ["", "-", "--", ".", "!", "?"]
        for f in self.yield_subcommands():
            for subc in f[0]:
                for p in prefix:
                    self.subcommands["{}{}".format(p, subc)] = f[1]

    def yield_subcommands(self):
        # yield ["help", "h"], self.unbound.localscan_help.run_command # ex
        return
        yield

    def get_subcommand_sync(self, m_text: str = ""):
        split_text = m_text.split(" ", 1)
        potential_subcommand = split_text[0]
        if len(potential_subcommand) == 0:
            return None, m_text
        else:
            matched_coro = self.subcommands.get(potential_subcommand.lower())
            if matched_coro is None:
                return None, m_text
            else:
                if len(split_text) == 2:
                    return matched_coro, split_text[1]
                else:
                    return matched_coro, ""

    async def get_subcommand_coro(self, m_text: str = ""):
        """returns the coro matching the subcommand and the string stripped of the subcommand.
        Returns None and the original string if no subcommand match."""
        return await self.loop.run_in_executor(None, partial(self.get_subcommand_sync, m_text))

    @classmethod
    def mention(cls):
        return True

    @classmethod
    def embed_only(cls):
        return False

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
            async with (await LimitManager.cm_hp(d_message.channel)):
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
        raise InsightExc.userInput.EmbedPermissionRequired

    def can_text(self, d_message: discord.Message):
        return DiscordPermissionCheck.can_text(d_message)

    def can_embed(self, d_message: discord.Message):
        can_embed = DiscordPermissionCheck.can_embed(d_message)
        if self.embed_only() and not can_embed:
            raise InsightExc.DiscordError.DiscordPermissions("Insight is lacking the **embed links** and **send "
                                                             "messages** roles in this channel. You must enable "
                                                             "these roles before you can use this command.")
        return can_embed

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        if self.can_embed(d_message):
            async with (await LimitManager.cm_hp(d_message.channel)):
                embed = await self.get_embed(d_message, m_text)
                if self.mention():
                    await d_message.channel.send(content='{}\n'.format(d_message.author.mention), embed=embed)
                else:
                    await d_message.channel.send(embed=embed)
        elif self.can_text(d_message):
            text = await self.get_text(d_message, m_text)
            if self.mention():
                response_text = "{}\n{}".format(d_message.author.mention, text)
            else:
                response_text = "{}".format(text)
            if len(response_text) > 2000:
                response_text = response_text[:1850] + "\n!!Truncated - Enable embed links to get remainder of " \
                                                       "message through Discord rich embeds!!"
            async with (await LimitManager.cm_hp(d_message)):
                await d_message.channel.send(content=response_text)
        else:  # permissions error
            return

    async def run_command_proxy(self, d_message: discord.Message, m_text: str = ""):
        """Change function to do subcommand processing if any to change called command"""
        coro_subcommand, text_without_subcommand = await self.get_subcommand_coro(m_text)
        if coro_subcommand is None:
            await self.run_command(d_message, text_without_subcommand)
        else:
            await coro_subcommand(d_message, text_without_subcommand)

