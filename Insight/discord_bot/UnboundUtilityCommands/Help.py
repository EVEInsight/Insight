from .UnboundCommandBase import *


class Help(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.header = self.generate_header()
        self.commands = self.generate_commands()
        self.commands_as_list = self.generate_commands(as_list=True)
        self.prefix = self.generate_prefixes()
        self.links = self.generate_links()
        self.str_only = self.header + self.commands + self.prefix + self.links

    @classmethod
    def mention(cls):
        return False

    def generate_header(self):
        return "These are all of the available Insight commands. Note: Some commands may not be usable in all channel types and may require a feed service.\n\n"

    def generate_commands(self, as_list=False):
        s = ""
        commands = [
            "**{p}about** - Display Insight credits, version information, and bot invite links.",
            "**{p}admin** - Access the Insight admin console to execute administrator functionality.",
            "**{p}create** - Begin setting up a new feed service in this channel. Alias: **{p}new**",
            "**{p}8ball** - Shake the 8ball.",
            "**{p}help** - Display command information and prefixes.",
            "**{p}limits** - Display channel / server rate limits and usage stats.",
            "**{p}lock** - Lock a feed service from being modified by users without certain Discord channel roles.",
            "**{p}lscan** - Local scan. Copy and paste local pilots for a ship and affiliation overview.",
            "**{p}motd** - Display the current MOTD for Insight global announcements and updates.",
            "**{p}prefix** - Manage server-wide command prefixes for this bot.",
            "**{p}quit** - Close and shut down the Insight application service.",
            "**{p}remove** - Delete the currently configured feed service in this channel.",
            "**{p}roll** - Roll a random number between 0 and 100.",
            "**{p}settings** - Modify feed settings and behavior. Alias: **{p}config**",
            "**{p}start** - Start/resume a channel feed from being paused.",
            "**{p}status** - Display information about the currently running feed.",
            "**{p}stop** - Pause a channel feed.",
            "**{p}sync** - Manage contact EVE tokens for a radar or proximity watch feed. Contact token syncing "
            "allows you to ignore allies in tracked ships from appearing as potential targets.",
            "**{p}top** - List the most expensive kills over the last week.",
            "**{p}unlock** - Unlock a feed service to allow any Discord channel user to modify feed configuration."
        ]
        if as_list:
            return commands
        for c in commands:
            s += "{command}\n\n".format(command=c)
        return s

    def generate_prefixes(self):
        return "These are the currently configured prefixes for this server:\n{prefixes}\n"

    def generate_links(self):
        return "For more detailed command, feed type, or configuration information check out the project " \
             "[wiki](https://wiki.eveinsight.net).\nAdditional live support is available via the " \
             "[Insight support Discord server](https://discord.eveinsight.net).\n"

    async def get_prefix_str(self, d_message:discord.Message):
        set_pref_str = ""
        for p in (await self.serverManager.get_server_prefixes(d_message.channel)):
            set_pref_str += "**{}**\n".format(p)
        return set_pref_str

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs)->str:
        return self.str_only.format(p=await self.serverManager.get_min_prefix(d_message.channel),
                                    prefixes=await self.get_prefix_str(d_message))

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs):
        e = discord.Embed()
        e.color = discord.Color(659493)
        e.timestamp = datetime.datetime.utcnow()
        e.set_author(name=self.__class__.__name__)
        e.set_footer(text='Utility command')
        e.description = self.header
        min_prefix = await self.serverManager.get_min_prefix(d_message.channel)
        field_value = ""
        field_length = 0
        for s in self.commands_as_list:
            input_str = s.format(p=min_prefix)
            str_len = len(input_str)
            field_length += str_len
            if field_length > 1000:
                e.add_field(name="Commands", value=field_value, inline=False)
                field_value = ""
                field_length = str_len
            field_value += "{command_str}\n".format(command_str=input_str)
        if field_length != 0:
            e.add_field(name="Commands", value=field_value, inline=False)
        e.add_field(name="Prefixes", value=self.prefix.format(prefixes=await self.get_prefix_str(d_message)), inline=False)
        e.add_field(name="Additional help", value=self.links, inline=False)
        return e


