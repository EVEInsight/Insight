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
import InsightLogger
import logging


class Discord_Insight_Client(discord.Client):
    def __init__(self, service_module, multiproc_dict):
        super().__init__(fetch_offline_members=True, heartbeat_timeout=20)
        self.logger = InsightLogger.InsightLogger.get_logger('Insight.main', 'Insight_main.log', console_print=True,
                                                             console_level=logging.INFO)
        self.service: service_module = service_module
        self.__multiproc_dict: dict = multiproc_dict
        self.channel_manager: service.Channel_manager = self.service.channel_manager
        self.channel_manager.set_client(self)
        self.commandLookup = DiscordCommands()
        self.background_tasks = background_tasks(self)
        self.threadpool_insight = ThreadPoolExecutor(max_workers=5)
        self.threadpool_zk = ThreadPoolExecutor(max_workers=2)
        self.threadpool_unbound = ThreadPoolExecutor(max_workers=1)
        self.unbound_commands = UnboundUtilityCommands(self)
        self.loop.set_default_executor(self.threadpool_insight)
        self.loop.create_task(self.setup_tasks())
        self.__id_semaphores = {}
        self.__id_create_locks = {}

    async def on_ready(self):
        print('-------------------')
        print('Logged in as: {}'.format(str(self.user.name)))
        invite_url = 'https://discordapp.com/api/oauth2/authorize?client_id={}&permissions=149504&scope=bot'.format(
            self.user.id)
        print('Invite Link: {}'.format(invite_url))
        print('This bot is a member of {} servers.'.format(str(len(self.guilds))))
        print('Loaded Discord cache with: {} servers, {} channels, {} users.'.format(len(self.guilds),
                                                                        len(list(self.get_all_channels())),
                                                                        len(self.users)))
        print("Use 'CTRL-C' to shut down Insight from the console or run the '!quit' command from any Discord channel.")
        print('-------------------')

    async def setup_tasks(self):
        await self.wait_until_ready()
        try:
            game_act = discord.Activity(name="Starting...", type=discord.ActivityType.watching)
            await self.change_presence(activity=game_act, status=discord.Status.dnd)
        except Exception as ex:
            print(ex)
        await self.service.zk_obj.make_queues()
        self.loop.create_task(self.service.zk_obj.pull_kms_ws())
        await self.channel_manager.load_channels()
        await self.post_motd()
        self.loop.create_task(self.service.zk_obj.pull_kms_redisq())
        self.loop.create_task(self.background_tasks.setup_backgrounds())
        self.loop.create_task(self.service.zk_obj.coroutine_filters(self.threadpool_zk))
        await self.loop.run_in_executor(None, self.service.zk_obj.debug_simulate)
        self.loop.create_task(self.service.zk_obj.coroutine_process_json(self.threadpool_zk))
        self.loop.create_task(self.channel_manager.auto_refresh())
        self.loop.create_task(self.channel_manager.auto_channel_refresh())

    async def post_motd(self):
        div = '================================='
        motd = (div + '\nInsight server message of the day:\n\n{}\n'.format(str(self.service.motd)) + div)
        print(motd)
        if self.service.motd:
            await self.loop.run_in_executor(None, partial(self.channel_manager.post_message, motd))

    def cleanup_close(self):
        print('Closing event loop...')
        asyncio.get_event_loop().close()
        print('Closing Insight thread pool...')
        self.threadpool_insight.shutdown(wait=True)
        print('Closing zKillboard thread pool...')
        self.threadpool_zk.shutdown(wait=True)
        self.threadpool_unbound.shutdown(wait=True)
        self.service.shutdown()
        print('Insight successfully shut down.')

    async def shutdown_self(self):
        try:
            game_act = discord.Activity(name="Shutting down...", type=discord.ActivityType.watching)
            await self.change_presence(activity=game_act, status=discord.Status.dnd)
        except Exception as ex:
            print(ex)
        await self.logout()

    async def reboot_self(self):
        self.__multiproc_dict['flag_reboot'] = True
        await self.shutdown_self()

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

    async def get_create_lock(self, channel_object) ->asyncio.Lock:
        try:
            assert channel_object.id is not None
            cLock = self.__id_create_locks.get(channel_object.id)
            if not isinstance(cLock, asyncio.Lock):
                cLock = asyncio.Lock()
                self.__id_create_locks[channel_object.id] = cLock
            return cLock
        except Exception as ex:
            print('Error when getting create lock: {}'.format(ex))
            return asyncio.Lock()

    async def on_guild_join(self, guild: discord.Guild):
        self.logger.info('Joined server ({}) with {} members.'.format(guild.name, guild.member_count))
        channel: discord.TextChannel = guild.system_channel
        if channel is not None:
            permissions: discord.Permissions = channel.permissions_for(channel.guild.me)
            message = "Hi!\n\nI am an EVE Online killmail streaming bot offering various feed types and " \
                      "utilities. Run the **!create** command in a Discord channel to quickly begin setting up a feed." \
                      " Run the **!help** command to see all of my available commands. You can read more about my " \
                      "functionality and follow development on [GitHub](https://github.com/Nathan-LS/Insight).\n\n" \
                      "Thank you for choosing Insight!"
            if permissions.embed_links and permissions.send_messages:
                embed = discord.Embed()
                embed.title = ""
                embed.color = discord.Color(659493)
                embed.set_author(name='Insight welcome message')
                embed.description = message
                await channel.send(embed=embed)
            elif permissions.send_messages:
                message = message.replace('**', "'")
                message = message.replace('[GitHub]', " ")
                await channel.send(content=message)
            else:
                return

    async def on_guild_remove(self, guild: discord.Guild):
        self.logger.info('Removed from server ({}) with {} members.'.format(guild.name, guild.member_count))

    async def on_message(self, message):
        await self.wait_until_ready()
        if message.author.id == self.user.id or message.author.bot:
            return
        if not await self.commandLookup.is_command(message):
            return
        sem = await self.get_semaphore(message.channel)
        async with sem:
            try:
                feed = await self.channel_manager.get_channel_feed(message.channel)
                if await self.commandLookup.create(message):
                    loc = await self.get_create_lock(message.channel)
                    async with loc:
                        feed = await self.channel_manager.get_channel_feed(message.channel)
                        await feed.proxy_lock(feed.command_create(message), message.author, 1)
                elif await self.commandLookup.settings(message):
                    await feed.proxy_lock(feed.command_settings(message), message.author, 1)
                elif await self.commandLookup.start(message):
                    await feed.proxy_lock(feed.command_start(message), message.author, 1)
                elif await self.commandLookup.stop(message):
                    await feed.proxy_lock(feed.command_stop(message), message.author, 1)
                elif await self.commandLookup.sync(message):
                    await feed.proxy_lock(feed.command_sync(message), message.author, 1)
                elif await self.commandLookup.remove(message):
                    await feed.proxy_lock(feed.command_remove(message), message.author, 1)
                elif await self.commandLookup.help(message):
                    await feed.proxy_lock(feed.command_help(message), message.author, 0)
                elif await self.commandLookup.about(message):
                    await feed.proxy_lock(feed.command_about(message), message.author, 0)
                elif await self.commandLookup.status(message):
                    await feed.proxy_lock(feed.command_status(message), message.author, 1)
                elif await self.commandLookup.lock(message):
                    await feed.proxy_lock(feed.command_lock(message), message.author, 1, ignore_channel_setting=True)
                elif await self.commandLookup.unlock(message):
                    await feed.proxy_lock(feed.command_unlock(message), message.author, 1, ignore_channel_setting=True)
                elif await self.commandLookup.quit(message):
                    await feed.proxy_lock(feed.command_quit(message), message.author, 2, ignore_channel_setting=True)
                elif await self.commandLookup.admin(message):
                    await feed.proxy_lock(feed.command_admin(message), message.author, 2, ignore_channel_setting=True)
                elif await self.commandLookup.eightball(message):
                    await feed.proxy_lock(feed.command_8ball(message), message.author, 0)
                elif await self.commandLookup.dscan(message):
                    await feed.proxy_lock(feed.command_dscan(message), message.author, 0)
                else:
                    await self.commandLookup.notfound(message)
                await asyncio.sleep(3)
            except InsightExc.InsightException as ex:
                try:
                    await message.channel.send("{}\n{}".format(message.author.mention, str(ex)))
                except:
                    pass
                await asyncio.sleep(20)
            except discord.Forbidden:
                if isinstance(message.channel, discord.TextChannel) and \
                        message.channel.permissions_for(message.channel.guild.me).send_messages:
                    try:
                        msg = "Insight received a permission error. Ensure Insight has the correct permissions in this channel as listed on the project Git page. https://github.com/Nathan-LS/Insight#permissions"
                        await message.channel.send("{}\n{}".format(message.author.mention, msg))
                    except:
                        pass
                await asyncio.sleep(30)
            except discord.NotFound:
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                try:
                    await message.channel.send("{}\nInsight is shutting down. This coroutine has been canceled."
                                               .format(message.author.mention))
                except:
                    pass
            except Exception as ex:
                traceback.print_exc()
                try:
                    await message.channel.send(
                        "{}\nUncaught exception: '{}'.".format(message.author.mention, str(ex.__class__.__name__)))
                except:
                    pass
                await asyncio.sleep(20)

    @staticmethod
    def start_bot(service_module, multiproc_dict):
        if service_module.config_file["discord"]["token"]:
            client = Discord_Insight_Client(service_module, multiproc_dict)
            try:
                client.run(service_module.config_file["discord"]["token"])
                client.cleanup_close()
            except KeyboardInterrupt:
                client.cleanup_close()
        else:
            print("Missing a Discord Application token. Please make sure to set this variable in the config file '{}'".format(service_module.cli_args.config))
            sys.exit(1)
