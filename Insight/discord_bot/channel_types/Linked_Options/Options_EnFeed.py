from . import Base_Feed
import discord
from discord_bot.channel_types import enFeed
from discord_bot.OptionLogic.EntityOptions import *


class Options_EnFeed(Base_Feed.base_activefeed):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, enFeed.enFeed)
        super().__init__(insight_channel)

    def yield_options(self):
        yield (self.InsightOptionRequired_add, True)
        yield (self.InsightOption_remove, False)
        yield (self.InsightOptionRequired_tracktype, True)
        yield (self.InsightOptionRequired_trackpods, True)
        yield (self.InsightOption_minValue, False)
        yield (self.InsightOption_maxValue, False)
        yield (self.InsightOption_addShipBlackList, False)
        yield (self.InsightOption_removeShipBlackList, False)
        yield from super().yield_options()

    async def InsightOptionRequired_add(self, message_object:discord.Message):
        """Add a new tracked entity  - Add an entity (pilot, corp, or alliance) to track involved PvP activity. You can add more than 1 entity to a channel."""
        await AddEntityOption(self.cfeed, message_object).run()

    async def InsightOption_remove(self,message_object:discord.Message):
        """Remove a tracked entity - Remove tracking of PvP activity for a previously added pilot, corp, or alliance."""
        await RemoveEntityOption(self.cfeed, message_object).run()

    async def InsightOptionRequired_tracktype(self, message_object:discord.Message):
        """Show losses/kills  - Set the feed to one of three modes: show losses only, show kills only, or show both kills and losses."""
        await SetTrackTypOption(self.cfeed, message_object).run()

    async def InsightOptionRequired_trackpods(self, message_object: discord.Message):
        """Display POD(capsule) kills/losses - Set the feed to either ignore or display POD mails."""
        await SetTrackPodsOption(self.cfeed, message_object).run()

    async def InsightOption_minValue(self, message_object: discord.Message):
        """Set minimum ISK value - Set the minimum ISK value for killmails."""
        await MinValueOption(self.cfeed, message_object).run()

    async def InsightOption_maxValue(self, message_object: discord.Message):
        """Set maximum ISK value - Set the maximum ISK value for killmails."""
        await MaxValueOption(self.cfeed, message_object).run()

    async def InsightOption_addShipBlackList(self, message_object: discord.Message):
        """Add ship to blacklist - null"""
        await AddShipOption(self.cfeed, message_object).run()

    async def InsightOption_removeShipBlackList(self, message_object: discord.Message):
        """Remove a ship from blacklist - null"""
        await RemoveShipOption(self.cfeed, message_object).run()


