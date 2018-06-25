from . import options_base
import discord
import discord_bot as bot


class Options_EnFeed(options_base.Options_Base):
    """InsightOption_  InsightOptionRequired_"""

    async def InsightOptionRequired_add(self, message_object:discord.Message):
        """Add tracking  - Adds a pilot, corp, or alliance to show involved kms in this feed"""
        await message_object.channel.send("Not Implemented")

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

    async def InsightOptionRequired_tracktype(self, message_object:discord.Message):
        """Show losses/kills  - Set the feed to one of three modes for tracked entities: show losses only,
        show kills only, show both kills and losses
        """
        await message_object.channel.send("Not Implemented")
