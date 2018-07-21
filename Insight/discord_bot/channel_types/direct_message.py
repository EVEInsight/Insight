from . import base_object as inCh
from .base_object import *
import discord


class direct_message(inCh.discord_feed_service):
    def __init__(self,channel_discord_object:discord.DMChannel, service_object):
        super(direct_message, self).__init__(channel_discord_object, service_object)
        assert isinstance(channel_discord_object, discord.DMChannel)
        self.user_id = self.channel_discord_object.recipient.id
        self.setup_table()

    def get_linked_options(self):
        return Linked_Options.opt_dm(self)

    def get_object_id(self):
        return self.user_id

    async def command_sync(self, message_object):
        """!sync - Manage your configured contact tokens settings. Add, delete, and update your tokens."""
        await self.command_settings(message_object)

    @classmethod
    def linked_table(cls):
        return dbRow.tb_users

    def __str__(self):
        return "Direct Message"


from . import Linked_Options
