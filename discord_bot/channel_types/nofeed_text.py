from . import base_object as inCh
from . import capRadar as inCR
from .base_object import *
from . import Linked_Options


class discord_text_nofeed_exist(Linked_Options.opt_base):
    def __init__(self,channel_discord_object:discord.TextChannel, service_module):
        super(discord_text_nofeed_exist, self).__init__(channel_discord_object,service_module)

    async def test_function(self):
        await self.channel_discord_object.send("ok")

    async def command_create(self, message_object):
        __options = insightClient.mapper_index(self.discord_client, message_object)
        __options.set_main_header("This is a test")
        __options.add_option(insightClient.option_calls_coroutine("capRadar", "A fully customizable feed with the ability to track supers and stuff", inCR.capRadar.create_new(message_object,self.service,self.discord_client)))
        await __options()

    @classmethod
    def command_not_supported(cls, command:str):
        return "The command '{}' is not supported by a channel with no feed services created.\nRun the command '!create' to set up a new feed.\n\n{}".format(command,cls.str_more_help())

    @classmethod
    async def create_new(cls,message_object:discord.Message, service_module, discord_client):
        __tmp_feed_object:cls = await cls.load_new(message_object.channel,service_module,discord_client)
        try:
            async for option in __tmp_feed_object.all_options_required():
                await option(message_object)
            await service_module.channel_manager.add_feed_object(__tmp_feed_object)
            await message_object.channel.send("Created a new feed!")
        except Exception as ex:
            print(ex)
            await __tmp_feed_object.delete()
            await message_object.channel.send("Something went wrong when creating a new feed")

    @classmethod
    def channel_id_is_feed(cls, id, service_module):
        return cls.linked_table().exists(id,service_module)

    @classmethod
    def get_existing_feed_type(cls,ch_id,service_object):
        if inCR.capRadar.channel_id_is_feed(ch_id,service_object):
            return inCR.capRadar
        else:
            return None
