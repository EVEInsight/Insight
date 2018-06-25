from . import base_object as inCh
from .base_object import *


class direct_message(inCh.discord_feed_service):
    def __init__(self,channel_discord_object:discord.DMChannel, service_object):
        super(direct_message, self).__init__(channel_discord_object, service_object)

    def make_table(self):
        pass

    @classmethod
    def command_not_supported_sendmessage(cls, command:str):
        return "The command '{}' is not supported in direct messages. The ability to set up feeds in direct messages is not supported.\n\n{}".format(command,cls.str_more_help())