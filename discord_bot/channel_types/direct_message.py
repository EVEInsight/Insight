from discord_bot.channel_types.base_object import *
from discord_bot.discord_main import *


class discord_text_nofeed_exist(discord_feed_service):
    def __init__(self,channel_discord_object:discord.DMChannel, service_object):
        assert isinstance(channel_discord_object,discord.DMChannel)
        self.channel_discord_object = channel_discord_object
        self.channel_id = channel_discord_object.id
        self.service = service_object

        self.kmQueue = queue.Queue()
        self.messageQueue = queue.Queue()

        self.make_table()

        # self.__update_table_discord_channel()
        # self.__load_tables()

    def make_table(self):
        pass

    @classmethod
    def command_not_supported(cls, command:str):
        return "The command '{}' is not supported in direct messages. The ability to set up feeds in direct messages is not supported.\n\n{}".format(command,cls.str_more_help())