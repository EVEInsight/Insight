import queue
import discord_bot as insightClient
import asyncio
import random
import discord
from functools import partial
import service as Service
import database.db_tables as dbRow
from sqlalchemy.orm import Session


class discord_feed_service(object):
    def __init__(self,channel_discord_object:discord.TextChannel, service_object):
        assert isinstance(channel_discord_object,discord.TextChannel)
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
        #self.setup_table()
        #self.load_table()

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
        if self.linked_table().make_row(self.channel_id,self.service):
            pass
        else:
            raise None

    def load_table(self):
        self.cached_feed_table = self.general_table().get_row(self.channel_id, self.service)

    async def async_load_table(self):
        await self.discord_client.loop.run_in_executor(None,self.load_table)

    async def command_create(self, message_object):
        await self.command_not_supported_sendmessage(message_object)

    async def command_help(self,message_object):
        await self.command_not_supported_sendmessage(message_object)

    async def command_settings(self,message_object):
        __options = insightClient.mapper_index(self.discord_client,message_object)
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
            test = [i for i in range(1000)]
            test2 = [i for i in range(1000)]
            random.shuffle(test2)
            random.shuffle(test)
            __test = set(test)-set(test2)
            assert isinstance(km,dbRow.tb_kills)
            self.kmQueue.put_nowait(str("https://zkillboard.com/kill/{}/".format(str(km.kill_id))))

    def add_message(self,message_txt):
        if self.cached_feed_table.feed_running:
            self.kmQueue.put_nowait(str(message_txt))

    async def post_all(self):
        if self.cached_feed_table.feed_running:
            try:
                await self.channel_discord_object.send(self.kmQueue.get_nowait())
            except queue.Empty:
                pass
            except discord.Forbidden:
                await self.channel_manager.remove_feed(self.channel_id)

    async def remove(self):
        print("removed")

    def delete(self):
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

    @staticmethod
    def send_km(km,feed_channel):
        try:
            assert isinstance(km,dbRow.tb_kills)
            feed_channel.add_km(km)
        except Exception as ex:
            print(ex)

from . import Linked_Options

