from . import nofeed_text as noCH
from .base_object import *
from . import Linked_Options


class capRadar(noCH.discord_text_nofeed_exist,Linked_Options.opt_capradar):
    def __init__(self, channel_discord_object: discord.TextChannel, service_module):
        super(capRadar, self).__init__(channel_discord_object, service_module)
        self.setup_table()
        self.load_table()

    def __str__(self):
        return "Capital Radar Feed"

    @classmethod
    def linked_table(cls):
        return dbRow.tb_capRadar

    @classmethod
    async def create_new(cls,message_object:discord.Message, service_module, discord_client):
        """Cap Radar - A feed service that tracks hostile supercapital,capital, or blops activity with range of a specific system"""
        await super(capRadar, cls).create_new(message_object,service_module,discord_client)