from .base_object import *
import itertools


class discord_text_nofeed_exist(discord_feed_service):
    def load_table(self):
        if not type(self) == discord_text_nofeed_exist:
            super().load_table()

    def setup_table(self):
        if not type(self) == discord_text_nofeed_exist:
            super().setup_table()

    async def command_create(self, message_object):
        """!create - Begin setting up a new channel feed service in this channel."""
        if not type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            __options = insightClient.mapper_index(self.discord_client,message_object)
            __options.set_main_header("Select the new type of KM feed to wish to create in this channel")
            __options.add_header_row("Fully customizable feed services")
            __options.add_option(insightClient.option_calls_coroutine(name=inCR.capRadar.create_new.__doc__,coroutine_object=inCR.capRadar.create_new(message_object,self.service,self.discord_client)))
            __options.add_option(insightClient.option_calls_coroutine(name=inEF.enFeed.create_new.__doc__,coroutine_object=inEF.enFeed.create_new(message_object,self.service,self.discord_client)))
            __options.add_header_row("Preconfigured template feeds")
            for subc in itertools.chain(inEF.enFeed.__subclasses__(), inCR.capRadar.__subclasses__()):
                __options.add_option(insightClient.option_calls_coroutine(name=subc.get_template_desc(),
                                                                          coroutine_object=subc.create_new(
                                                                              message_object, self.service,
                                                                              self.discord_client)))
            await __options()

    async def command_settings(self,message_object):
        """!settings - Modify feed settings for a channel."""
        if type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            await super(discord_text_nofeed_exist, self).command_settings(message_object)

    async def command_start(self,message_object:discord.Message):
        """!start - Starts/resumes a channel feed from being paused."""
        if type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            if not self.cached_feed_table.feed_running:
                try:
                    await self.discord_client.loop.run_in_executor(None,partial(dbRow.tb_channels.set_feed_running,self.channel_id,True,self.service))
                    await self.async_load_table()
                    await message_object.channel.send("Feed service started")
                except Exception as ex:
                    await message_object.channel.send("Something went wrong when running this command.\n\nException: {}".format(str(ex)))
            else:
                await message_object.channel.send(
                    "{}\nThe channel feed is already running".format(message_object.author.mention))

    async def command_stop(self,message_object:discord.Message):
        """!stop - Pauses a channel feed temporarily."""
        if type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            if self.cached_feed_table.feed_running:
                try:
                    await self.discord_client.loop.run_in_executor(None,partial(dbRow.tb_channels.set_feed_running,self.channel_id,False,self.service))
                    await self.async_load_table()
                    await message_object.channel.send("Feed service stopped")
                except Exception as ex:
                    await message_object.channel.send("Something went wrong when running this command.\n\nException: {}".format(str(ex)))
            else:
                await message_object.channel.send("{}\nThe channel feed is already stopped".format(message_object.author.mention))

    async def command_remove(self,message_object:discord.Message):
        """!remove - Delete the currently configured feed service in this channel."""
        if type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            __question = insightClient.mapper_return_yes_no(self.discord_client, message_object)
            __question.set_main_header("Are you sure to want to remove this channel feed, deleting all configured settings?\n")
            if await __question():
                if await self.channel_manager.delete_feed(self.channel_id):
                    await message_object.channel.send("Successfully deleted this channel feed.")
                else:
                    await message_object.channel.send("Something went wrong when removing the channel.")
            else:
                await message_object.channel.send("No changes were made")

    def __str__(self):
        return "channel with no feed"

    @classmethod
    async def create_new(cls,message_object:discord.Message, service_module, discord_client):
        __tmp_feed_object:cls = await cls.load_new(message_object.channel,service_module,discord_client)
        try:
            async for option in __tmp_feed_object.linked_options.get_option_coroutines(required_only=True):
                await option(message_object)
            await service_module.channel_manager.add_feed_object(__tmp_feed_object)
            await message_object.channel.send("Created a new feed!")
            await __tmp_feed_object.command_start(message_object)
            try:
                channel_name = str(message_object.channel.name)
                server_name = str(message_object.channel.guild.name)
                print('New {} in {}({})'.format(str(__tmp_feed_object), channel_name, server_name))
            except Exception as ex:
                print(ex)
        except Exception as ex:
            await __tmp_feed_object.delete()
            await message_object.channel.send(
                "Something went wrong when creating a new feed. Run the command '!create' "
                "to start over.")
            raise ex

    @classmethod
    def channel_id_is_feed(cls, id, service_module):
        return cls.linked_table().exists(id,service_module)

    @classmethod
    def get_template_subclass(cls, ch_id, service_module):
        db: Session = service_module.get_session()
        try:
            row = db.query(cls.linked_table()).filter(cls.linked_table().channel_id == ch_id).one()
            template_id = row.template_id
            for subc in cls.__subclasses__():
                if subc.get_template_id() == template_id:
                    return subc
            return cls
        except Exception as ex:
            print(ex)
            return cls
        finally:
            db.close()

    @classmethod
    def get_existing_feed_type(cls,ch_id,service_object):
        if inCR.capRadar.channel_id_is_feed(ch_id,service_object):
            return inCR.capRadar.get_template_subclass(ch_id, service_object)
        elif inEF.enFeed.channel_id_is_feed(ch_id,service_object):
            return inEF.enFeed.get_template_subclass(ch_id, service_object)
        else:
            return None

    def get_linked_options(self):
        return Linked_Options.opt_blankchannel(self)

    @classmethod
    def get_template_id(cls):
        return 0


from . import Linked_Options
from . import capRadar as inCR
from . import enFeed as inEF