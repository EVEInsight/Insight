import queue
import discord_bot as insightClient
import asyncio
import random
import discord
from functools import partial
import service as Service
import database.db_tables as dbRow
from sqlalchemy.orm import Session
from .FiltersVisualsEmbedded import *
import InsightExc
from sqlalchemy.orm.exc import NoResultFound


class discord_feed_service(object):
    def __init__(self,channel_discord_object:discord.TextChannel, service_object):
        assert isinstance(service_object,Service.ServiceModule)
        self.channel_discord_object = channel_discord_object
        self.channel_id = channel_discord_object.id
        self.service = service_object
        self.channel_manager = self.service.channel_manager
        self.discord_client = self.service.channel_manager.get_discord_client()

        self.kmQueue = queue.Queue()
        self.messageQueue = queue.Queue()
        self.__deque_task = None
        self.linked_options = self.get_linked_options()
        self.setup_table()
        self.template_loader()
        self.load_table()

    def set_deque_task(self,deq_task:asyncio.Task):
        assert isinstance(deq_task,asyncio.Task)
        self.__deque_task = deq_task

    def deque_done(self):
        try:
            assert isinstance(self.__deque_task,asyncio.Task)
            return self.__deque_task.done()
        except AssertionError:
            return True

    def setup_table(self):
        """make the related table if it does not yet exist"""
        if self.linked_table().make_row(self.get_object_id(), self.service, self.get_template_id()):
            pass
        else:
            raise InsightExc.Db.DatabaseError

    def get_object_id(self):
        return self.channel_id

    def load_table(self):
        self.cached_feed_table:dbRow.tb_channels = self.general_table().get_row(self.channel_id, self.service)
        # must be set to sqlalchemy channel specific object ex self.cached_feed_specific.object_enfeed

    def template_loader(self):
        pass

    async def async_load_table(self):
        await self.discord_client.loop.run_in_executor(None,self.load_table)

    async def command_create(self, message_object):
        await self.command_not_supported_sendmessage(message_object)

    async def command_sync(self, message_object):
        await self.command_not_supported_sendmessage(message_object)

    async def command_about(self, message_object):
        """!about - Display Insight credits and version info."""
        msg = "Insight {} by Nathan-LS. An EVE Online killmail feed" \
              " bot for Discord.\n\nhttps://github.com/Nathan-LS/Insight".format(str(self.service.get_version()))
        await message_object.channel.send(msg)

    async def command_help(self,message_object):
        """!help - Displays information about available commands."""

        def get_commands():
            for i in dir(self):
                if i.startswith("command_"):
                    yield getattr(self, i)
                else:
                    continue

        resp_str = "These are all commands and their descriptions available to be used:\n\n"
        for i in get_commands():
            info = i.__doc__
            if info is not None:
                resp_str += "{}\n\n".format(info)
        resp_str += "\nFor more detailed information, check out the project wiki:\nhttps://github.com/Nathan-LS/Insight/wiki"
        await message_object.channel.send("{}\n{}".format(message_object.author.mention, resp_str))

    async def command_settings(self,message_object):
        """!settings - Modify Insight settings related to this channel or user."""
        __options = insightClient.mapper_index_withAdditional(self.discord_client,message_object)
        __options.set_main_header("Select an option to modify:")
        async for cor in self.linked_options.get_option_coroutines():
            __options.add_option(insightClient.option_calls_coroutine(cor.__doc__,"",cor(message_object)))
        await __options()

    async def command_start(self,message_object:discord.Message):
        await self.command_not_supported_sendmessage(message_object)

    async def command_stop(self,message_object:discord.Message):
        await self.command_not_supported_sendmessage(message_object)

    async def command_remove(self,message_object:discord.Message):
        await self.command_not_supported_sendmessage(message_object)

    def add_km(self,km):
        if self.cached_feed_table.feed_running:
            assert isinstance(km,dbRow.tb_kills)
            __visual = self.linked_visual(km)
            if __visual:
                self.kmQueue.put_nowait(__visual)

    def add_message(self,message_text):
        if self.cached_feed_table.feed_running:
            self.kmQueue.put_nowait(message_text)

    def linked_visual(self,km_row):
        raise NotImplementedError
        #return visual_enfeed(km_row,self.channel_discord_object,self.cached_feed_table,self.cached_feed_specific)

    async def post_all(self):
        if self.cached_feed_table.feed_running:
            try:
                __item = self.kmQueue.get_nowait()
                if isinstance(__item, base_visual):
                    await __item()
                    await self.channel_manager.add_delay(__item.get_load_time())
                else:
                    await self.channel_discord_object.send(str(__item))
            except queue.Empty:
                pass
            except discord.Forbidden:
                try:
                    await self.channel_discord_object.send(
                        "Permissions are incorrectly set for the bot. See https://github.com/Nathan-LS/Insight#permissions\n\n\nOnce permissions are correctly set, run the command '!start to resume the feed.'")
                except:
                    pass
                finally:
                    await self.channel_manager.remove_feed(self.channel_id)
            except discord.HTTPException as ex:
                if ex.status == 404:  # channel deleted
                    await self.channel_manager.remove_feed(self.channel_id)
            except Exception as ex:
                print(ex)

    async def remove(self):
        print("feed removed")

    async def delete(self):
        def non_async_delete():
            db:Session = self.service.get_session()
            try:
                __row = db.query(dbRow.tb_channels).filter(dbRow.tb_channels.channel_id == self.channel_id).one()
                db.delete(__row)
                db.commit()
                return True
            except Exception as ex:
                print(ex)
                db.rollback()
                return False
            finally:
                db.close()
        return await self.discord_client.loop.run_in_executor(None,non_async_delete)

    async def command_not_supported_sendmessage(self, message_object:discord.Message):
        await message_object.channel.send("{}\nThis command is not supported in channel of type: {}\n".format(message_object.author.mention,str(self)))

    @classmethod
    def str_more_help(cls):
        return "For assistance, run the command '!help' to see a list of available commands and their functions or visit:\n\nhttps://github.com/Nathan-LS/Insight"

    def __str__(self):
        return "Base Insight Object"

    @classmethod
    def general_table(cls)->dbRow.tb_channels:
        return dbRow.tb_channels

    @classmethod
    def linked_table(cls)->dbRow.tb_discord_base:
        raise NotImplementedError

    def get_linked_options(self):
        return Linked_Options.opt_base(self)

    @classmethod
    async def load_new(cls,channel_object:discord.TextChannel,service_module, discord_client):
        assert isinstance(channel_object,discord.TextChannel)
        return await discord_client.loop.run_in_executor(None, partial(cls,channel_object,service_module))

    @classmethod
    def get_template_id(cls):
        return None  # no template id exists

    @classmethod
    def get_template_desc(cls):
        return ""

    @staticmethod
    def send_km(km,feed_channel):
        try:
            assert isinstance(km,dbRow.tb_kills)
            feed_channel.add_km(km)
        except Exception as ex:
            print(ex)


from . import Linked_Options


