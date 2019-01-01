from .UnboundCommandBase import *
import InsightUtilities


class Prefix(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.commands = InsightUtilities.InsightCommands()

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs):
        prefixes = await self.unbound.serverManager.get_server_prefixes(d_message.channel)
        msg = "These are the currently configured prefixes for the server. All commands must begin with one of " \
              "the following prefixes for Insight to recognize a command.\n\n"
        for p in prefixes:
            msg += '{}\n'.format(p)
        return msg

    async def option_add(self, d_message: discord.Message):
        pass

    async def option_remove(self, d_message: discord.Message):
        pass

    async def option_view(self, d_message: discord.Message):
        await super().run_command(d_message)

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        options = dOpt.mapper_index_withAdditional(self.client, d_message)
        options.set_main_header("This is the prefix management menu. Here you can add and remove prefixes that "
                                "Insight will respond to. Prefix settings are Discord server-wide and affect all "
                                "channels. If you delete all prefixes you can still return to this menu by prefixing a "
                                "command with '{0}'.\n Example: {0} prefix".format(self.client.user.mention))
        options.add_option(dOpt.option_calls_coroutine("Add - Add a new prefix that the bot will respond to.", "",
                                                       self.option_add(d_message)))
        options.add_option(dOpt.option_calls_coroutine("Remove - Remove a previously added or default command prefix.",
                                                       "", self.option_remove(d_message)))
        options.add_option(dOpt.option_calls_coroutine("View - View currently configured prefixes for this server.", "",
                                                       self.option_view(d_message)))
        await options()
