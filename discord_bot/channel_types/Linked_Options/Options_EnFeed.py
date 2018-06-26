from . import Base_Feed
import discord
from discord_bot import discord_options
from database.db_tables import id_resolver
from functools import partial


class Options_EnFeed(Base_Feed.base_activefeed):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, enFeed.enFeed)
        super().__init__(insight_channel)

    async def InsightOptionRequired_add(self, message_object:discord.Message):
        __search = discord_options.mapper_return_noOptions(self.cfeed.discord_client,message_object,timeout_seconds=60)
        __search.set_main_header("Enter the name of an entity you wish to track in this feed.\n\n"
                                 "An entity is a pilot, corporation, or alliance in which this channel "
                                 "will streams kms involving.")
        __search.set_footer_text("Enter a name. Note: partial names are accepted: ")
        __selected = None
        while __selected is None:
            __en_select = discord_options.mapper_index(self.cfeed.discord_client, message_object, timeout_seconds=120)
            __en_select:discord_options.mapper_index = await self.cfeed.discord_client.loop.run_in_executor(None,partial(id_resolver.make_options,__en_select,await __search()))
            __en_select.add_header_row("More Options")
            __en_select.add_option(discord_options.option_returns_object("Search again", return_object=None))
            __selected = await __en_select()
        print(__selected)

    async def InsightOption_remove(self,message_object:discord.Message):
        """Remove tracking  - Removes tracking of km involvement for a pilot, corp, or alliance from """
        await message_object.channel.send("Not Implemented")

    async def InsightOptionRequired_tracktype(self, message_object:discord.Message):
        """Show losses/kills  - Set the feed to one of three modes for tracked entities: show losses only,
        show kills only, show both kills and losses
        """
        await message_object.channel.send("Not Implemented")

    async def InsightOptionRequired_track_deployable(self, message_object:discord.Message):
        """Track deployables  - Set if the feed should track KMs of deployables (mobile depots, cyno inhibs, etc)
        """
        await message_object.channel.send("Not Implemented")


from .. import enFeed
