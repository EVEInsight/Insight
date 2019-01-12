from .UnboundCommandBase import *
import InsightUtilities
from functools import partial
import discord
import InsightExc


class Prefix(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.commands = InsightUtilities.InsightCommands()
        self.serverManager = self.unbound.serverManager

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs):
        prefixes = await self.serverManager.get_server_prefixes(d_message.channel)
        msg = "These are the currently configured prefixes for the server. All commands must begin with one of " \
              "the following prefixes for Insight to recognize a command:\n\n"
        for p in prefixes:
            msg += '{}\n'.format(p)
        return msg

    async def option_add(self, d_message: discord.Message):
        max_pref = 5
        if len(await self.serverManager.get_server_prefixes(d_message.channel)) > max_pref:
            raise InsightExc.userInput.InsightException("There are too many prefixes configured for this server. "
                                                        "You are only allowed a maximum of {} custom prefixes. Please "
                                                        "remove unneeded prefixes before adding more.".format(max_pref))
        options = dOpt.mapper_return_noOptions(self.client, d_message)
        max_prefix_len = 20
        options.set_main_header("Enter a new command prefix to add for this Discord server. A new prefix is a short "
                                "symbol or string at the beginning of a command. By adding a prefix, all Insight "
                                "commands will be recognized when used with your custom prefix. The maximum "
                                "prefix length possible is {}.\n\nExample: Adding the prefix: '&' will allow "
                                "Insight to respond to '&help'.".format(max_prefix_len))
        new_prefix = await options()
        if len(new_prefix) > max_prefix_len:
            return
        await self.serverManager.add_prefix(new_prefix, d_message.channel.guild)
        await self.option_view(d_message)

    async def option_remove(self, d_message: discord.Message):
        options = dOpt.mapper_index_withAdditional(self.client, d_message)
        options.set_main_header("Select an Insight prefix to remove for this Discord server.")
        for p in (await self.serverManager.get_server_prefixes(d_message.channel)):
            if p != self.client.user.mention:
                options.add_option(dOpt.option_returns_object(str(p), "", p))
        remove_prefix: str = await options()
        await self.serverManager.remove_prefix(remove_prefix, d_message.channel.guild)
        await self.option_view(d_message)

    async def option_view(self, d_message: discord.Message):
        await super().run_command(d_message)

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        if not isinstance(d_message.channel, discord.TextChannel):
            raise InsightExc.userInput.InsightException("Prefix modification is not available for this channel type.")
        options = dOpt.mapper_index_withAdditional(self.client, d_message)
        options.set_main_header("This is the prefix management menu. Here you can add and remove prefixes that "
                                "Insight will respond to. Prefix settings are Discord server-wide and affect all "
                                "channels. Prefixes reduce command collision with other Discord bots that may also "
                                "use the same prefixes. If you delete all prefixes you can still return to this menu "
                                "by prefixing a command with '{0}'.\n Example: {0} prefix".format(self.client.user.mention))
        options.add_option(dOpt.option_calls_coroutine("Add - Add a new prefix that the bot will respond to.", "",
                                                       self.option_add(d_message)))
        options.add_option(dOpt.option_calls_coroutine("Remove - Remove a previously added or default command prefix.",
                                                       "", self.option_remove(d_message)))
        options.add_option(dOpt.option_calls_coroutine("View - View currently configured prefixes for this server.", "",
                                                       self.option_view(d_message)))
        await options()
