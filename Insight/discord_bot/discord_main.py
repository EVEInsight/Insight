import discord
from concurrent.futures import ThreadPoolExecutor
import service
from .background_tasks import background_tasks
from .DiscordCommands import DiscordCommands
import sys
from functools import partial
import InsightExc
import traceback
from .UnboundUtilityCommands import UnboundUtilityCommands
import asyncio


class Discord_Insight_Client(discord.Client):
    def __init__(self, service_module):
        super().__init__(fetch_offline_members=True, heartbeat_timeout=20)
        self.service: service_module = service_module
        self.channel_manager: service.Channel_manager = self.service.channel_manager
        self.channel_manager.set_client(self)
        self.commandLookup = DiscordCommands()
        self.background_tasks = background_tasks(self)
        self.unbound_commands = UnboundUtilityCommands(self)
        self.loop.set_default_executor(ThreadPoolExecutor(max_workers=5))
        self.loop.create_task(self.setup_tasks())
        self.__id_semaphores = {}

    async def on_ready(self):
        print('-------------------')
        print('Logged in as: {}'.format(str(self.user.name)))
        invite_url = 'https://discordapp.com/api/oauth2/authorize?client_id={}&permissions=149504&scope=bot'.format(
            self.user.id)
        print('Invite Link: {}'.format(invite_url))
        print('This bot is a member of {} servers.'.format(str(len(self.guilds))))
        print('-------------------')

    async def setup_tasks(self):
        await self.wait_until_ready()
        try:
            game_act = discord.Activity(name="Starting...", type=discord.ActivityType.watching)
            await self.change_presence(activity=game_act, status=discord.Status.dnd)
        except Exception as ex:
            print(ex)
        self.loop.create_task(self.service.zk_obj.pull_kms_redisq())
        self.loop.create_task(self.service.zk_obj.pull_kms_ws())
        await self.channel_manager.load_channels()
        await self.post_motd()
        self.loop.create_task(self.background_tasks.setup_backgrounds())
        self.loop.create_task(self.km_process())
        self.loop.create_task(self.km_deque_filter())
        self.loop.create_task(self.channel_manager.auto_refresh())
        self.loop.create_task(self.channel_manager.auto_channel_refresh())

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

    async def get_semaphore(self, channel_object) ->asyncio.Semaphore:
        try:
            assert channel_object.id is not None
            cSem = self.__id_semaphores.get(channel_object.id)
            if not isinstance(cSem, asyncio.Semaphore):
                cSem = asyncio.Semaphore(value=3)
                self.__id_semaphores[channel_object.id] = cSem
            return cSem
        except Exception as ex:
            print('Error when getting semaphore: {}'.format(ex))
            return asyncio.Semaphore(value=3)

    async def on_message(self, message):
        await self.wait_until_ready()
        try:
            if message.author.id == self.user.id or message.author.bot:
                return
            if not await self.commandLookup.is_command(message):
                return
            sem = await self.get_semaphore(message.channel)
            async with sem:
                if await self.commandLookup.create(message):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await feed.proxy_lock(feed.command_create(message), message.author, 1)
                elif await self.commandLookup.settings(message):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await feed.proxy_lock(feed.command_settings(message), message.author, 1)
                elif await self.commandLookup.start(message):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await feed.proxy_lock(feed.command_start(message), message.author, 1)
                elif await self.commandLookup.stop(message):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await feed.proxy_lock(feed.command_stop(message), message.author, 1)
                elif await self.commandLookup.sync(message):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await feed.proxy_lock(feed.command_sync(message), message.author, 1)
                elif await self.commandLookup.remove(message):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await feed.proxy_lock(feed.command_remove(message), message.author, 1)
                elif await self.commandLookup.help(message):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await feed.proxy_lock(feed.command_help(message), message.author, 0)
                elif await self.commandLookup.about(message):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await feed.proxy_lock(feed.command_about(message), message.author, 0)
                elif await self.commandLookup.status(message):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await feed.proxy_lock(feed.command_status(message), message.author, 1)
                elif await self.commandLookup.lock(message):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await feed.proxy_lock(feed.command_lock(message), message.author, 1, ignore_channel_setting=True)
                elif await self.commandLookup.unlock(message):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await feed.proxy_lock(feed.command_unlock(message), message.author, 1, ignore_channel_setting=True)
                elif await self.commandLookup.eightball(message):
                    await self.unbound_commands.command_8ball(message)
                elif await self.commandLookup.dscan(message):
                    await self.unbound_commands.command_dscan(message)
                else:
                    await self.commandLookup.notfound(message)
                    await asyncio.sleep(3)
        except Exception as ex:
            if isinstance(ex, InsightExc.InsightException):
                try:
                    await message.channel.send("{}\n{}".format(message.author.mention, str(ex)))
                except:
                    pass
            elif isinstance(ex, discord.Forbidden):
                pass  # cant send error message anyway
            elif isinstance(ex, discord.NotFound):
                pass  # channel deleted
            else:
                traceback.print_exc()
                try:
                    await message.channel.send(
                        "{}\nUncaught exception: '{}'.".format(message.author.mention, str(ex.__class__.__name__)))
                except:
                    pass
        await asyncio.sleep(2)

    @staticmethod
    def start_bot(service_module):
        if service_module.config_file["discord"]["token"]:
            client = Discord_Insight_Client(service_module)
            client.run(service_module.config_file["discord"]["token"])
        else:
            print("Missing a Discord Application token. Please make sure to set this variable in the config file '{}'".format(service_module.cli_args.config))
            sys.exit(1)
