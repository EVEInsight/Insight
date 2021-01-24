from .Time import Time
import discord
import datetime
from InsightUtilities.EmbedLimitedHelper import EmbedLimitedHelper
from InsightUtilities.StaticHelpers.URLHelper import URLHelper


class TimeHelp(Time):
    @classmethod
    def embed_only(cls):
        return True

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        prefix = await self.serverManager.get_min_prefix(d_message.channel)
        e = EmbedLimitedHelper()
        e.set_color(discord.Color(0x49b0b6))
        e.set_timestamp(datetime.datetime.utcnow())
        e.set_author(name="Command Overview for Time", icon_url=URLHelper.type_image(3764, 64))
        e.set_description(description="The time command displays time information for EVE and global timezones.")
        e.field_buffer_start("Usage Instructions", "Usage Instructions")
        e.field_buffer_add("The basic usage of this command is **'{}time'**".format(prefix))
        e.field_buffer_end()
        e.field_buffer_start("Additional command aliases", "Additional command aliases")
        command_a = ["time", "et", "date", "datetime", "clock", "evetime"]
        aliases_command = ""
        for a in command_a:
            aliases_command += "\n{}{}".format(prefix, a)
        e.field_buffer_add("This command can be called through the following aliases:"
                           "{}".format(aliases_command))
        e.field_buffer_end()
        e.field_buffer_start("Subcommand and Modifier Flags", "Subcommand and Modifier Flags")
        e.field_buffer_add("Time supports modifier flags for displaying additional output.\n"
                           "Subcommands can be prefixed with one of the following characters: '-', '--', '.', '!', '?'")
        e.field_buffer_end_bounds()
        e.field_buffer_start_bounds("```", "```")
        e.field_buffer_add("\t--\tNo arguments or flags given. Displays the current EVE Online / UTC time.")
        e.field_buffer_add("\t\tUsage: {}time\n\n".format(prefix))
        e.field_buffer_add("\t-world\tDisplay the current time across various time zones.")
        e.field_buffer_add("\t\tUsage: {}time world".format(prefix))
        e.field_buffer_add("\t\tAliases: 'world', 'w'\n\n")
        e.field_buffer_add("\t-h\tDisplay this help menu.")
        e.field_buffer_add("\t\tUsage: {}time help".format(prefix))
        e.field_buffer_add("\t\tAliases: 'help', 'h'\n\n")
        e.field_buffer_end_bounds()
        e.field_buffer_end()
        return e
