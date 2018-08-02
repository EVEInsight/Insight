import discord
from concurrent.futures import ThreadPoolExecutor
import service
from .background_tasks import background_tasks
from .DiscordCommands import DiscordCommands
import sys
from functools import partial
import InsightExc
import traceback


class Discord_Insight_Client(discord.Client):
    def __init__(self,service_module):
        super().__init__()
        self.service: service_module = service_module
        self.channel_manager: service.Channel_manager = self.service.channel_manager
        self.commandLookup = DiscordCommands()
        self.background_tasks = background_tasks(self)
        self.loop.set_default_executor(ThreadPoolExecutor(max_workers=6))
        self.loop.create_task(self.setup_tasks())

    async def on_ready(self):
        print('-------------------')
        print('Logged in as: {}'.format(str(self.user.name)))
        invite_url = 'https://discordapp.com/api/oauth2/authorize?client_id={}&permissions=149504&scope=bot'.format(
            self.user.id)
        print('Invite Link: {}'.format(invite_url))
        print('This bot is a member of:')
        print('Servers: {}'.format(str(len(self.guilds))))
        print('Channels: {}'.format(str(len(list(self.get_all_channels())))))
        print('-------------------')

    async def setup_tasks(self):
        await self.wait_until_ready()
        await self.channel_manager.set_client(self)
        await self.channel_manager.load_channels()
        await self.post_motd()
        self.__task_backgrounds = self.loop.create_task(self.background_tasks.setup_backgrounds())
        self.__task_km_process = self.loop.create_task(self.km_process())
        self.__task_km_deque_filter = self.loop.create_task(self.km_deque_filter())
        self.__task_km_deque = self.loop.create_task(self.channel_manager.post_all_queued())
        self.__task_km_enqueue = self.loop.create_task(self.km_enqueue())

    async def km_enqueue(self):
        await self.wait_until_ready()
        await self.loop.run_in_executor(None, self.service.zk_obj.thread_pull_km)

    async def km_process(self):
        await self.wait_until_ready()
        await self.loop.run_in_executor(None, self.service.zk_obj.thread_process_json)

    async def km_deque_filter(self):
        await self.wait_until_ready()
        await self.loop.run_in_executor(None, self.service.zk_obj.thread_filters)

    async def post_motd(self):
        div = '=================================\n'
        motd = (div + 'Insight server message of the day:\n\n{}\n'.format(str(self.service.motd)) + div)
        print(motd)
        if self.service.motd:
            await self.loop.run_in_executor(None, partial(self.channel_manager.post_message, motd))

    async def on_message(self, message):
        await self.wait_until_ready()
        try:
            if message.author.id == self.user.id:
                return
            if not await self.commandLookup.is_command(message):
                return
            elif await self.commandLookup.create(message):
                await (await self.channel_manager.get_channel_feed(message.channel)).command_create(message)
            elif await self.commandLookup.settings(message):
                await (await self.channel_manager.get_channel_feed(message.channel)).command_settings(message)
            elif await self.commandLookup.start(message):
                await (await self.channel_manager.get_channel_feed(message.channel)).command_start(message)
            elif await self.commandLookup.stop(message):
                await (await self.channel_manager.get_channel_feed(message.channel)).command_stop(message)
            elif await self.commandLookup.sync(message):
                await (await self.channel_manager.get_channel_feed(message.channel)).command_sync(message)
            elif await self.commandLookup.remove(message):
                await (await self.channel_manager.get_channel_feed(message.channel)).command_remove(message)
            elif await self.commandLookup.help(message):
                await (await self.channel_manager.get_channel_feed(message.channel)).command_help(message)
            elif await self.commandLookup.about(message):
                await (await self.channel_manager.get_channel_feed(message.channel)).command_about(message)
            elif await self.commandLookup.status(message):
                await (await self.channel_manager.get_channel_feed(message.channel)).command_status(message)
            else:
                await self.commandLookup.notfound(message)
        except Exception as ex:
            if isinstance(ex, InsightExc.InsightException):
                try:
                    await message.channel.send("{}\n{}".format(message.author.mention, str(ex)))
                except:
                    return
            elif isinstance(ex, discord.Forbidden):
                return  # cant send error message anyway
            else:
                print(traceback.print_exc())

    @staticmethod
    def start_bot(service_module):
        if service_module.config_file["discord"]["token"]:
            client = Discord_Insight_Client(service_module)
            client.run(service_module.config_file["discord"]["token"])
        else:
            print("Missing a Discord Application token. Please make sure to set this variable in the config file '{}'".format(service_module.cli_args.config))
            sys.exit(1)
