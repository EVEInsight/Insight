from . import nofeed_text as noCH
from .base_object import *


class capRadar(noCH.discord_text_nofeed_exist):
    def __init__(self, channel_discord_object: discord.TextChannel, service_module):
        super(capRadar, self).__init__(channel_discord_object, service_module)
        self.sync_settings = Linked_Options.opt_sync(self)

    def __str__(self):
        return "Capital Radar Feed"

    def load_table(self):
        super(capRadar, self).load_table()
        self.cached_feed_specific = self.cached_feed_table.object_capRadar

    def linked_visual(self, km_row):
        return visual_capradar(km_row, self.channel_discord_object, self.cached_feed_table, self.cached_feed_specific,
                               self)

    @classmethod
    def linked_table(cls):
        return dbRow.tb_capRadar

    @classmethod
    async def create_new(cls,message_object:discord.Message, service_module, discord_client):
        """Capital Radar - Tracks hostile super, capital, or blops activity within a set lightyear proximity of base systems. Radar feeds are ideal for tracking hostile incursions into friendly space, hunting expensive targets within jump range, or detecting capital escalations."""
        await super(capRadar, cls).create_new(message_object,service_module,discord_client)

    async def command_sync(self, message_object):
        """!sync - Manage contact EVE tokens for this channel. Contact tokens allow you to ignore allies in tracked ships from appearing on radar."""
        __options = insightClient.mapper_index_withAdditional(self.discord_client, message_object)
        __options.set_main_header("Select an option to modify:")
        async for cor in self.sync_settings.get_option_coroutines():
            __options.add_option(insightClient.option_calls_coroutine(cor.__doc__, "", cor(message_object)))
        await __options()

    async def background_contact_sync(self, message=None):
        await self.sync_settings.InsightOption_syncnow(message)

    def get_linked_options(self):
        return Linked_Options.opt_capradar(self)


from . import Linked_Options