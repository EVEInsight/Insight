from . import nofeed_text as noCH
from .base_object import *


class capRadar(noCH.discord_text_nofeed_exist):
    def __init__(self, channel_discord_object: discord.TextChannel, service_module):
        super(capRadar, self).__init__(channel_discord_object, service_module)
        self.setup_table()
        self.load_table()

    def __str__(self):
        return "Capital Radar Feed"

    def load_table(self):
        super(capRadar, self).load_table()
        self.cached_feed_specific = self.cached_feed_table.object_capRadar

    def add_km(self,km):
        pass

    def linked_visual(self,km_row):
        return visual_capradar(km_row, self.channel_discord_object, self.cached_feed_table, self.cached_feed_specific)

    @classmethod
    def linked_table(cls):
        return dbRow.tb_capRadar

    @classmethod
    async def create_new(cls,message_object:discord.Message, service_module, discord_client):
        """Cap Radar - A feed service that tracks hostile supercapital,capital, or blops activity with range of a specific system"""
        await super(capRadar, cls).create_new(message_object,service_module,discord_client)

    def get_linked_options(self):
        return Linked_Options.opt_capradar(self)


from . import Linked_Options