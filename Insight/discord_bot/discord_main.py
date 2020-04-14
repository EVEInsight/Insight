import discord
from concurrent.futures import ThreadPoolExecutor
import service
from .background_tasks import background_tasks
from InsightUtilities import LimitManager
import InsightUtilities
import sys
from functools import partial
import InsightExc
from .UnboundUtilityCommands import UnboundUtilityCommands
import asyncio
import InsightLogger
import logging
import os


class Discord_Insight_Client(discord.Client):
    def __init__(self, service_module):
        super().__init__(fetch_offline_members=True, heartbeat_timeout=20)
        self.logger = InsightLogger.InsightLogger.get_logger('Insight.main', 'Insight_main.log', console_print=True,
                                                             console_level=logging.INFO)
        self.service: service_module = service_module
        self.channel_manager: service.Channel_manager = self.service.channel_manager
        self.channel_manager.set_client(self)
        self.serverManager = service.ServerManager(self.service, self)
        self.commandLookup = InsightUtilities.InsightCommands()
        self.background_tasks = background_tasks(self)
        self.threadpool_insight = ThreadPoolExecutor(max_workers=6)
        self.threadpool_zk = ThreadPoolExecutor(max_workers=2)
        self.threadpool_unbound = ThreadPoolExecutor(max_workers=1)
        self.unbound_commands = UnboundUtilityCommands(self)
        self.loop.set_default_executor(self.threadpool_insight)
        self.loop.create_task(self.setup_tasks())
        self.channelLocks = InsightUtilities.AsyncLockManager(self.loop)
        self.channelSemaphores = InsightUtilities.AsyncSemaphoreManager(self.loop)
        self.limiter = LimitManager()

    def get_invite_url(self):
        try:
            return 'https://discordapp.com/api/oauth2/authorize?client_id={}&permissions=149504&scope=bot' \
                   ''.format(self.user.id)
        except:
            return ""

    async def on_ready(self):
        print('-------------------')
        print('Logged in as: {}'.format(str(self.user.name)))
        print('Invite Link: {}'.format(self.get_invite_url()))
        print('This bot is a member of {} servers.'.format(str(len(self.guilds))))
        print('Loaded Discord cache with: {} servers, {} channels, {} users.'.format(len(self.guilds),
                                                                        len(list(self.get_all_channels())),
                                                                        len(self.users)))
        print("Use 'CTRL-C' to shut down Insight from the console or run the '!quit' command from any Discord channel. "
              "Alternative options: Send SIGINT signal to the Insight process or run 'docker stop ContainerID' for a "
              "graceful shutdown.".format(os.getpid()))
        print('-------------------')

    async def setup_tasks(self):
        await self.wait_until_ready()
        try:
            game_act = discord.Activity(name="Starting...", type=discord.ActivityType.watching)
            await self.change_presence(activity=game_act, status=discord.Status.dnd)
        except Exception as ex:
            print(ex)
        await self.serverManager.loader()
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

    async def close(self):
        try:
            print("===========Received signal to shut down.===========")
            print("Logging out from Discord...")
            await super().close()
            print("Done")
            print('Closing Insight thread pool...')
            self.threadpool_insight.shutdown(wait=True)
            print("Done")
            print('Closing zKillboard thread pool...')
            self.threadpool_zk.shutdown(wait=True)
            print("Done")
            print('Closing zKillboard thread pool...')
            self.threadpool_unbound.shutdown(wait=True)
            print("Done")
            print("Closing service module and database connections...")
            self.service.shutdown()
            print("Done")
            print('Insight was successfully shut down.')
            lg = InsightLogger.InsightLogger.get_logger('main', 'main.log')
            lg.info('Insight is shutting down with a clean exit.')
            sys.exit(0)
        except Exception as ex:
            print(ex)
            sys.exit(1)

    async def on_guild_join(self, guild: discord.Guild):
        self.logger.info('Joined server ({}) with {} members.'.format(guild.name, guild.member_count))
        channel: discord.TextChannel = guild.system_channel
        if channel is not None:
            permissions: discord.Permissions = channel.permissions_for(channel.guild.me)
            message = "Hi!\n\nI am an EVE Online killmail streaming bot offering various feed types and " \
                      "utilities. Run the **!create** command in a Discord channel to quickly begin setting up a feed." \
                      " Run the **!help** command to see all of my available commands. Use the **!prefix** " \
                      "command to configure server-wide command prefixes. You can read more about my " \
                      "functionality and follow development on [GitHub](https://github.com/Nathan-LS/Insight).\n\n" \
                      "Thank you for choosing Insight!"
            if permissions.embed_links and permissions.send_messages:
                embed = discord.Embed()
                embed.title = ""
                embed.color = discord.Color(659493)
                embed.set_author(name='Insight welcome message')
                embed.description = message
                async with (await LimitManager.cm(channel)):
                    await channel.send(embed=embed)
            elif permissions.send_messages:
                message = message.replace('**', "'")
                message = message.replace('[GitHub]', " ")
                async with (await LimitManager.cm(channel)):
                    await channel.send(content=message)
            else:
                return

    async def on_guild_remove(self, guild: discord.Guild):
        self.logger.info('Removed from server ({}) with {} members.'.format(guild.name, guild.member_count))

    async def on_message(self, message):
        await self.wait_until_ready()
        if message.author.id == self.user.id or message.author.bot:
            return
        if not await self.commandLookup.is_command_async(await self.serverManager.get_server_prefixes(message.channel), message.content, message.channel.id):
            return
        lg = InsightLogger.InsightLogger.get_logger('Insight.command.{}.{}'.format(str(type(message.channel)).replace(' ', ''),
                                                                           message.channel.id), 'Insight_command.log', child=True)
        async with (await self.channelSemaphores.get_object(message.channel.id, 3)):
            try:
                async with (await self.channelLocks.get_object(message.channel.id)):
                    feed = await self.channel_manager.get_channel_feed(message.channel)
                    await self.commandLookup.parse_and_run(message.channel.id, await self.serverManager.get_server_prefixes(message.channel), message.content,
                                                           create=feed.proxy_lock(feed.command_create(message), message.author, 1),
                                                           settings=feed.proxy_lock(feed.command_settings(message), message.author, 1),
                                                           start=feed.proxy_lock(feed.command_start(message), message.author, 1),
                                                           stop=feed.proxy_lock(feed.command_stop(message), message.author, 1),
                                                           sync=feed.proxy_lock(feed.command_sync(message), message.author, 1),
                                                           remove=feed.proxy_lock(feed.command_remove(message), message.author, 1),
                                                           help=feed.proxy_lock(feed.command_help(message), message.author, 0),
                                                           about=feed.proxy_lock(feed.command_about(message), message.author, 0),
                                                           status=feed.proxy_lock(feed.command_status(message), message.author, 1),
                                                           lock=feed.proxy_lock(feed.command_lock(message), message.author, 1, ignore_channel_setting=True),
                                                           unlock=feed.proxy_lock(feed.command_unlock(message), message.author, 1, ignore_channel_setting=True),
                                                           quit=feed.proxy_lock(feed.command_quit(message), message.author, 2, ignore_channel_setting=True),
                                                           admin=feed.proxy_lock(feed.command_admin(message), message.author, 2, ignore_channel_setting=True),
                                                           eightball=feed.proxy_lock(feed.command_8ball(message), message.author, 0),
                                                           dscan=feed.proxy_lock(feed.command_dscan(message), message.author, 0),
                                                           prefix=feed.proxy_lock(feed.command_prefix(message), message.author, 1, ignore_channel_setting=True),
                                                           limits=feed.proxy_lock(feed.command_limits(message), message.author, 1),
                                                           roll=feed.proxy_lock(feed.command_roll(message), message.author, 0))
                await asyncio.sleep(3)
            except InsightExc.InsightException as ex:
                lg.exception(ex)
                try:
                    async with (await LimitManager.cm(message)):
                        await message.channel.send("{}\n{}".format(message.author.mention, str(ex)))
                except:
                    pass
                await asyncio.sleep(30)
            except discord.Forbidden as ex:
                lg.exception(ex)
                if isinstance(message.channel, discord.TextChannel) and \
                        message.channel.permissions_for(message.channel.guild.me).send_messages:
                    try:
                        msg = "Insight received a permission error. Ensure Insight has the correct permissions in this channel as listed on the project Git page. https://github.com/Nathan-LS/Insight#permissions"
                        async with (await LimitManager.cm(message)):
                            await message.channel.send("{}\n{}".format(message.author.mention, msg))
                    except:
                        pass
                await asyncio.sleep(30)
            except discord.NotFound as ex:
                lg.exception(ex)
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                try:
                    async with (await LimitManager.cm_hp(message)):
                        await message.channel.send("{}\nInsight is shutting down. This coroutine has been canceled."
                                                   .format(message.author.mention))
                except:
                    pass
            except Exception as ex:
                lg.exception(ex)
                try:
                    async with (await LimitManager.cm(message)):
                        await message.channel.send(
                            "{}\nUncaught exception: '{}'.".format(message.author.mention, str(ex.__class__.__name__)))
                except:
                    pass
                await asyncio.sleep(20)

    @staticmethod
    def start_bot(service_module):
        if service_module.config.get("DISCORD_TOKEN"):
            client = Discord_Insight_Client(service_module)
            client.run(service_module.config.get("DISCORD_TOKEN"))
        else:
            print("Missing a Discord Application token. Please make sure to set this variable in the config file '{}'".format(service_module.cli_args.config))
            sys.exit(1)
