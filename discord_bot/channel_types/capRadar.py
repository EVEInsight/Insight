from discord_bot.channel_types.base_object import *
from discord_bot.channel_types import *


class capRadar(discord_feed_service):
    def __init__(self, channel_discord_object: discord.TextChannel, service_module):
        super(capRadar, self).__init__(channel_discord_object, service_module)

    @classmethod
    def linked_table(cls):
        return tb_capRadar