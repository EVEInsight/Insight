from . import nofeed_text as inCh
from .base_object import *


class capRadar(inCh.discord_text_nofeed_exist):
    def __init__(self, channel_discord_object: discord.TextChannel, service_module):
        super(capRadar, self).__init__(channel_discord_object, service_module)
        self.setup_table()
        self.load_table()

    @classmethod
    def linked_table(cls):
        return dbRow.tb_capRadar