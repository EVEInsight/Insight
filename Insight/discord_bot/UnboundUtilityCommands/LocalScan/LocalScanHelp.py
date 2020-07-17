from .LocalScan import LocalScan
import discord
import datetime
from InsightUtilities.EmbedLimitedHelper import EmbedLimitedHelper
from InsightUtilities.StaticHelpers.URLHelper import URLHelper


class LocalScanHelp(LocalScan):
    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        e = EmbedLimitedHelper()
        e.set_color(discord.Color(659493))
        e.set_timestamp(datetime.datetime.utcnow())
        e.set_author(name="Command Overview for Local Scan", icon_url=URLHelper.type_image(1973, 64))
        e.set_description(description="Local scan is an Insight utility that estimates the current ships for pilots "
                                      "in local. This tool looks up the previous kill and loss activity for pilots "
                                      "and displays the last active ship along with the time delay from last "
                                      "activity. \nPilots where last activity was a loss are noted.")
        e.field_buffer_start("Usage Instructions", "Usage Instructions")
        e.field_buffer_add("The basic usage of this command is **'!s *LOCAL_SCAN*'**\n*LOCAL_SCAN* is the copied scan "
                           "of all pilots in local from the game.\n\n**Copying local instructions:**\n"
                           "1. Select a single pilot in local chat\n2. Use **CTRL** + **A** to select all of local\n"
                           "3. Use **CTRL** + **C** to copy all pilots in local\n4. Use **CTRL** + **V** to "
                           "paste the pilot list into Discord with the scan command\n\nNote: Sometimes local "
                           "exceeds the Discord character limit and it will give you an option to upload the paste "
                           "as a text file. At this time, Insight does not support parsing text files for local scan "
                           "so you may need to select a subset of local using **SHIFT** to analyze.")
        e.field_buffer_end()
        e.field_buffer_start("Subcommand and Modifier Flags", "Subcommand and Modifier Flags")
        e.field_buffer_add("Local scan supports modifier flags for aggregating results and displaying output.\n"
                           "Subcommands can be prefixed with one of the following characters: '-', '--', '.', '!', '?'")
        e.field_buffer_end_bounds()
        e.field_buffer_start_bounds("```", "```")
        e.field_buffer_add("\t--\tNo arguments or flags given. Run a local scan and auto select a mode based on "
                           "length of local scan.")
        e.field_buffer_add("\t\tUsage: !scan LOCAL_SCAN\n\n")
        e.field_buffer_add("\t-s\tDisplay the ship type and pilot name for every entity in the local scan.")
        e.field_buffer_add("This mode is automatically selected when the scan contains a low count of pilots "
                           "unless another flag is explicitly used. \nPilots are listed by their affiliation "
                           "(corp or alliance) and affiliations are listed in order of total pilots belonging to "
                           "the affiliation in the scan. Pilots are further grouped by related systems and locations "
                           "within an affiliation grouping.\nWithin a affiliation grouping the involved killmail "
                           "links with the highest ratio of pilots from the scan are listed.")
        e.field_buffer_add("\t\tAliases: 'ships', 'pilots', 'p', 's'")
        e.field_buffer_add("\t\tUsage: !scan -s LOCAL_SCAN\n\n")
        e.field_buffer_add("\n\n")
        e.field_buffer_add("\t-a\tDisplay affiliations grouped by ship types. This mode displays a ship count overview "
                           "for every corp or alliance in the local scan and is automatically selected "
                           "for larger local scans unless another flag is specified.")
        e.field_buffer_add("\t\tAliases: 'affiliations', 'affiliation', 'groups', 'group', "
                           "'g', 'a'")
        e.field_buffer_add("\t\tUsage: !scan -a LOCAL_SCAN\n\n")
        e.field_buffer_add("\t-h\tDisplay this help command embed.")
        e.field_buffer_add("\t\tAliases: 'help', 'h'")
        e.field_buffer_add("\t\tUsage: !scan -h\n")
        e.field_buffer_end_bounds()
        e.field_buffer_end()
        return e

