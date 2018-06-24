from discord_bot.discord_main import *
from discord_bot.channel_types.base_object import *
from discord_bot.channel_types import *


class discord_text_nofeed_exist(discord_feed_service):
    def __init__(self,channel_discord_object:discord.TextChannel, service_module):
        super(discord_text_nofeed_exist, self).__init__(channel_discord_object,service_module)

    def setup_table(self):
        pass

    def load_table(self):
        pass

    async def test_function(self):
        await self.channel_discord_object.send("ok")

    async def command_create(self, message_object):
        __options = mapper_index(self.discord_client, message_object)
        __options.set_main_header("This is a test")
        __options.add_option(option_calls_coroutine("capRadar", "A fully customizable feed with the ability to track supers and stuff", insight_capRadar.create_new(message_object,self.service,self.discord_client)))
        await __options()

    @classmethod
    def command_not_supported(cls, command:str):
        return "The command '{}' is not supported by a channel with no feed services created.\nRun the command '!create' to set up a new feed.\n\n{}".format(command,cls.str_more_help())
