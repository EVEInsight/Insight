from . import options_base
import discord


class base_activefeed(options_base.Options_Base):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, nofeed_text.discord_text_nofeed_exist)
        super().__init__(insight_channel)

    "InsightOption_ InsightOptionRequired_"

    async def InsightOption_remove_opt(self,message_object:discord.Message):
        """Delete Feed  - Removes the currently active feed from this channel to be able to create a new,different one."""
        await self.cfeed.command_remove(message_object)

    async def InsightOption_pause(self,message_object:discord.Message):
        """Pause Feed  - Pauses the feed it is running currently"""
        await self.cfeed.command_stop(message_object)

    async def InsightOption_start(self,message_object:discord.Message):
        """Start feed  - Starts the feed it is currently paused"""
        await self.cfeed.command_start(message_object)

from .. import nofeed_text