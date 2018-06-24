import queue
from discord_bot.discord_main import *
import asyncio
import random


class discord_feed_service(object):
    def __init__(self,channel_discord_object:discord.TextChannel, service_object):
        assert isinstance(channel_discord_object,discord.TextChannel)
        #assert isinstance(service_object,service.service.service_module)
        self.channel_discord_object = channel_discord_object
        self.channel_id = channel_discord_object.id
        self.service = service_object
        self.channel_manager = self.service.channel_manager
        self.discord_client = self.service.channel_manager.get_discord_client()

        self.kmQueue = queue.Queue()
        self.messageQueue = queue.Queue()
        self.__deque_task = None

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

    async def command_help(self):
        await self.channel_discord_object.send(self.command_not_supported("!help"))

    async def command_create(self, message_object):
        await self.channel_discord_object.send(self.command_not_supported("!create"))

    async def command_start(self,message_object:discord.Message):
        if self.cached_feed_table.feed_running == False:
            try:
                await self.discord_client.loop.run_in_executor(None,partial(tb_channels.set_feed_running,self.channel_id,True,self.service))
                await self.async_load_table()
                await message_object.channel.send("Ok")
            except Exception as ex:
                await message_object.channel.send("Something went wrong when running this command.\n\nException: {}".format(str(ex)))
        else:
            await message_object.channel.send(
                "{}\nThe channel feed is already running".format(message_object.author.mention))

    async def command_stop(self,message_object:discord.Message):
        if self.cached_feed_table.feed_running == True:
            try:
                await self.discord_client.loop.run_in_executor(None,partial(tb_channels.set_feed_running,self.channel_id,False,self.service))
                await self.async_load_table()
                await message_object.channel.send("Ok")
            except Exception as ex:
                await message_object.channel.send("Something went wrong when running this command.\n\nException: {}".format(str(ex)))
        else:
            await message_object.channel.send("{}\nThe channel feed is already stopped".format(message_object.author.mention))

    async def command_remove(self,message_object:discord.Message):
        __question = mapper_return_yes_no(self.discord_client,message_object,timeout_seconds=40)
        __question.set_main_header("Are you sure to want to remove this channel feed, deleting all configured settings?\n")
        __question.set_footer_text("Enter either '1' for yes or '0' for no.")
        if await __question():
            if await self.channel_manager.delete_feed(self.channel_id):
                await message_object.channel.send("Successfully deleted this channel feed.")
            else:
                await message_object.channel.send("Something went wrong when removing the channel.")
        else:
            await message_object.channel.send("No changes were made")

    def add_km(self,km):
        if self.cached_feed_table.feed_running:
            test = [i for i in range(1000)]
            test2 = [i for i in range(1000)]
            random.shuffle(test2)
            random.shuffle(test)
            __test = set(test)-set(test2)
            assert isinstance(km,tb_kills)
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
            __row = db.query(tb_channels).filter(tb_channels.channel_id == self.channel_id).one()
            db.delete(__row)
            db.commit()
            return True
        except Exception as ex:
            print(ex)
            db.rollback()
            return False
        finally:
            db.close()

    async def option_sample(self,message_object:discord.Message):
        await message_object.channel.send("This is a sample option for the class. You should probably remove calls to it.")

    def all_options(self):
        return [self.option_sample]

    @classmethod
    def command_not_supported(cls, command:str):
        return "The command '{}' is not supported by this channel.\n\n{}'".format(command,cls.str_more_help())

    @classmethod
    def str_more_help(cls):
        return "For assistance, run the command '!help' to see a list of available commands and their functions or visit:\n\nhttps://github.com/Nathan-LS/Insight"

    @classmethod
    def general_table(cls)->tb_channels:
        return tb_channels

    @classmethod
    def linked_table(cls)->tb_discord_base:
        raise NotImplementedError

    @classmethod
    async def load_new(cls,channel_object:discord.TextChannel,service_module, discord_client):
        assert isinstance(channel_object,discord.TextChannel)
        return await discord_client.loop.run_in_executor(None, partial(cls,channel_object,service_module))

    @classmethod
    async def create_new(cls,message_object:discord.Message, service_module, discord_client):
        __tmp_feed_object:cls = await cls.load_new(message_object.channel,service_module,discord_client)
        try:
            for option in __tmp_feed_object.all_options():
                option:cls.option_sample
                await option(message_object)
            await service_module.channel_manager.add_feed_object(__tmp_feed_object)
            await message_object.channel.send("Created a new feed!")
        except Exception as ex:
            print(ex)
            await __tmp_feed_object.delete()
            await message_object.channel.send("Something went wrong when creating a new feed")

    @staticmethod
    def send_km(km,feed_channel):
        try:
            assert isinstance(km,tb_kills)
            feed_channel.add_km(km)
        except Exception as ex:
            print(ex)

