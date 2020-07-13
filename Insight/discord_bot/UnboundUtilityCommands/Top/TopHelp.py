from .Top import Top
import discord
import datetime
from InsightUtilities.EmbedLimitedHelper import EmbedLimitedHelper
from InsightUtilities.StaticHelpers.URLHelper import URLHelper


class TopHelp(Top):
    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        prefix = await self.serverManager.get_min_prefix(d_message.channel)
        e = EmbedLimitedHelper()
        e.set_color(discord.Color(659493))
        e.set_timestamp(datetime.datetime.utcnow())
        e.set_author(name="Command Overview for Top", icon_url=URLHelper.type_image(3764, 64))
        e.set_description(description="The top command displays the top losses for a given time period.")
        e.field_buffer_start("Usage Instructions", "Usage Instructions")
        e.field_buffer_add("The basic usage of this command is **'{}top'**".format(prefix))
        e.field_buffer_end()
        e.field_buffer_start("Subcommand and Modifier Flags", "Subcommand and Modifier Flags")
        e.field_buffer_add("Top supports modifier flags for aggregating results and displaying output.\n"
                           "Subcommands can be prefixed with one of the following characters: '-', '--', '.', '!', '?'")
        e.field_buffer_end_bounds()
        e.field_buffer_start_bounds("```", "```")
        e.field_buffer_add("\t--\tNo arguments or flags given. Displays the most expensive losses over the past week.")
        e.field_buffer_add("\t\tUsage: {}top\n\n".format(prefix))
        e.field_buffer_add("\t-y\tMost expensive losses over the past year.")
        e.field_buffer_add("\t\tUsage: {}top -y".format(prefix))
        e.field_buffer_add("\t\tAliases: 'year', 'y'\n\n")
        e.field_buffer_add("\t-m\tMost expensive losses over the past month.")
        e.field_buffer_add("\t\tUsage: {}top -m".format(prefix))
        e.field_buffer_add("\t\tAliases: 'month', 'm'\n\n")
        e.field_buffer_add("\t-w\tMost expensive losses over the past week.")
        e.field_buffer_add("\t\tUsage: {}top -w".format(prefix))
        e.field_buffer_add("\t\tAliases: 'week', 'w'\n\n")
        e.field_buffer_add("\t-d\tMost expensive losses over the past day.")
        e.field_buffer_add("\t\tUsage: {}top -d".format(prefix))
        e.field_buffer_add("\t\tAliases: 'day', 'd'\n\n")
        e.field_buffer_add("\t-hour\tMost expensive losses over the past hour.")
        e.field_buffer_add("\t\tUsage: {}top -hour".format(prefix))
        e.field_buffer_add("\t\tAliases: 'hour', '1h'\n\n")
        e.field_buffer_add("\t-h\tDisplay this help menu.")
        e.field_buffer_add("\t\tUsage: {}top -h".format(prefix))
        e.field_buffer_add("\t\tAliases: 'help', 'h'\n\n")
        e.field_buffer_end_bounds()
        e.field_buffer_end()
        return e

