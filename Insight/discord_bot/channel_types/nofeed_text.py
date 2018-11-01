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
        """!create - Begin setting up a new feed service in this channel."""
        if not type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            __options = insightClient.mapper_index_withAdditional(self.discord_client, message_object,
                                                                  timeout_seconds=300)
            __options.set_main_header("Select the new feed type you wish to add in this channel:")
            __options.add_header_row("Fully customizable feeds")
            __options.add_option(insightClient.option_calls_coroutine(name=inEF.enFeed.create_new.__doc__,coroutine_object=inEF.enFeed.create_new(message_object,self.service,self.discord_client)))
            __options.add_option(insightClient.option_calls_coroutine(name=inCR.capRadar.create_new.__doc__,coroutine_object=inCR.capRadar.create_new(message_object, self.service,self.discord_client)))
            for subc in itertools.chain(inEF.enFeed.__subclasses__(), inCR.capRadar.__subclasses__()):
                if not subc.is_preconfigured() and subc.feed_category() == 1:
                    __options.add_option(insightClient.option_calls_coroutine(name=subc.get_template_desc(),
                                                                              coroutine_object=subc.create_new(
                                                                                  message_object, self.service,
                                                                                  self.discord_client)))
            __options.add_header_row("Preconfigured/other feeds")
            for subc in itertools.chain(inEF.enFeed.__subclasses__(), inCR.capRadar.__subclasses__()):
                if subc.is_preconfigured() and subc.feed_category() == 1:
                    __options.add_option(insightClient.option_calls_coroutine(name=subc.get_template_desc(),
                                                                              coroutine_object=subc.create_new(
                                                                                  message_object, self.service,
                                                                                  self.discord_client)))
            await __options()

    async def command_settings(self,message_object):
        """!settings - Modify feed settings and behavior."""
        if type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            await super(discord_text_nofeed_exist, self).command_settings(message_object)

    async def command_start(self,message_object:discord.Message):
        """!start - Start/resume a channel feed from being paused."""
        if type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            if not self.cached_feed_table.feed_running:
                try:
                    await self.discord_client.loop.run_in_executor(None,partial(dbRow.tb_channels.set_feed_running,self.channel_id,True,self.service))
                    await self.async_load_table()
                    await message_object.channel.send("Feed service started.")
                except Exception as ex:
                    await message_object.channel.send("Something went wrong when running this command.\n\nException: {}".format(str(ex)))
            else:
                await message_object.channel.send(
                    "{}\nThe channel feed is already running.".format(message_object.author.mention))

    async def command_stop(self,message_object:discord.Message):
        """!stop - Pause a channel feed."""
        if type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            if self.cached_feed_table.feed_running:
                try:
                    await self.discord_client.loop.run_in_executor(None,partial(dbRow.tb_channels.set_feed_running,self.channel_id,False,self.service))
                    await self.async_load_table()
                    await message_object.channel.send("Feed service stopped.")
                except Exception as ex:
                    await message_object.channel.send("Something went wrong when running this command.\n\nException: {}".format(str(ex)))
            else:
                await message_object.channel.send(
                    "{}\nThe channel feed is already stopped.".format(message_object.author.mention))

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

    async def command_status(self, message_object: discord.Message):
        """!status - Display information about the currently running feed."""
        if type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            resp = "Feed type: {}\n".format(str(self))
            resp += "Currently running: {}\n".format(str(self.cached_feed_table.feed_running))
            await message_object.channel.send(resp)

    async def command_lock(self, message_object: discord.Message):
        """!lock - Lock a feed service from being modified by users without the Discord channel role: Manage Channel"""
        if type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            await self.linked_options.InsightOption_lockfeed(message_object)

    async def command_unlock(self, message_object: discord.Message):
        """!unlock - Unlock a previously locked feed service to allow any Discord channel user to modify configuration."""
        if type(self) == discord_text_nofeed_exist:
            await self.command_not_supported_sendmessage(message_object)
        else:
            await self.linked_options.InsightOption_unlockfeed(message_object)

    def __str__(self):
        return "channel with no feed"

    @classmethod
    async def create_new(cls,message_object:discord.Message, service_module, discord_client):
        __tmp_feed_object:cls = await cls.load_new(message_object.channel,service_module,discord_client)
        async with __tmp_feed_object.lock:
            try:
                await service_module.channel_manager.add_feed_object(__tmp_feed_object)
                async for option in __tmp_feed_object.linked_options.get_option_coroutines(required_only=True):
                    await option(message_object)
                await message_object.channel.send(
                    "Created a new feed! You can manage feed configuration and access additional settings with the "
                    "'!settings' command.")
                await __tmp_feed_object.command_start(message_object)
                print('New {} in {}'.format(str(__tmp_feed_object), __tmp_feed_object.str_channel_server()))
            except Exception as ex:
                await service_module.channel_manager.delete_feed(__tmp_feed_object.channel_id)
                try:
                    await message_object.channel.send(
                        "Something went wrong when creating a new feed. Run the command '!create' to start over.")
                except:
                    pass
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
            try:
                for subc in cls.__subclasses__():
                    if subc.get_template_id() == template_id:
                        return subc
                if isinstance(template_id, int) and template_id != 0:
                    return invalidF.InvalidFeed
            except Exception as ex:
                print(ex)
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
        return Linked_Options.opt_basicfeed(self)

    @classmethod
    def get_template_id(cls):
        return 0


from . import Linked_Options
from . import capRadar as inCR
from . import enFeed as inEF
from . import InvalidFeed as invalidF
