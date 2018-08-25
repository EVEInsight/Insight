from . import nofeed_text as noCH
from .base_object import *


class InvalidFeed(noCH.discord_text_nofeed_exist):
    def __init__(self, channel_discord_object: discord.TextChannel, service_module):
        super(InvalidFeed, self).__init__(channel_discord_object, service_module)
        self.add_message("The feed service that previously existed in this channel is invalid or is a discontinued "
                         "preconfigured feed type. The previous feed has been deleted and you may create a new feed "
                         "by running the '!create' command.")

    def setup_table(self):
        pass

    def __str__(self):
        return "Invalid Feed"

    def add_km(self, km):
        pass

    async def post_all(self):
        await super(InvalidFeed, self).post_all()
        await self.channel_manager.delete_feed(self.channel_id)
