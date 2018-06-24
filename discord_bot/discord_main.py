import discord
from service.service import *
import asyncio
import time
from service.service import *
from discord_bot.discord_options import *
from functools import partial
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor

class Discord_Insight_Client(discord.Client):
    #bot = commands.Bot(command_prefix="!")

    def __init__(self,service_module):
        super().__init__()
        self.service: service_module = service_module
        self.channel_manager: Channel_manager = self.service.channel_manager
        self.loop.set_default_executor(ThreadPoolExecutor(max_workers=5))
        self.loop.create_task(self.setup_tasks())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def setup_tasks(self):
        await self.wait_until_ready()
        await self.channel_manager.set_client(self)
        await self.channel_manager.load_channels()
        self.__task_km_enqueue = self.loop.create_task(self.km_enqueue())
        self.__task_km_deque_filter = self.loop.create_task(self.km_deque_filter())
        self.__task_km_deque = self.loop.create_task(self.channel_manager.post_all_queued())

    async def km_enqueue(self):
        await self.wait_until_ready()
        await self.loop.run_in_executor(None, self.service.zk_obj.pull_km)

    async def km_deque_filter(self):
        await self.wait_until_ready()
        await self.loop.run_in_executor(None,self.service.zk_obj.pass_to_filters)

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        elif message.content.startswith('!create'):
            await (await self.channel_manager.get_channel_feed(message.channel)).command_create(message)
        elif message.content.startswith('!start'):
            await (await self.channel_manager.get_channel_feed(message.channel)).command_start(message)
        elif message.content.startswith('!stop'):
            await (await self.channel_manager.get_channel_feed(message.channel)).command_stop(message)
        elif message.content.startswith('!remove'):
            await (await self.channel_manager.get_channel_feed(message.channel)).command_remove(message)


    @staticmethod
    def start_bot(service_module):
        if service_module.config_file["discord"]["token"]:
            client = Discord_Insight_Client(service_module)
            client.run(service_module.config_file["discord"]["token"])
        else:
            print("Missing a Discord Application token. Please make sure to set this variable in the config file '{}'".format(service_module.cli_args.config))
            exit(1)