from . import nofeed_text as noCh
from .base_object import *


class enFeed(noCh.discord_text_nofeed_exist):
    def __init__(self, channel_discord_object: discord.TextChannel, service_module):
        super().__init__(channel_discord_object, service_module)
        self.setup_table()
        self.load_table()

    @classmethod
    def linked_table(cls):
        return dbRow.tb_enfeed

    def __str__(self):
        return "Entity Feed"

    @classmethod
    async def create_new(cls,message_object:discord.Message, service_module, discord_client):
        """Entity Feed  - A general feed that posts kills/losses involving selected entities(pilots,corps,alliances)"""
        await super().create_new(message_object,service_module,discord_client)

    def get_linked_options(self):
        return Linked_Options.opt_enfeed(self)

from . import Linked_Options