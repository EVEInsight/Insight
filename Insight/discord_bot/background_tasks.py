import discord
import asyncio
from functools import partial
import psutil
import datetime
import requests
import json
import aiohttp
import traceback
import time
import InsightLogger
import InsightUtilities


class background_tasks(object):
    def __init__(self, insight_client):
        assert isinstance(insight_client, discord_bot.Discord_Insight_Client)
        self.client: discord_bot.Discord_Insight_Client = insight_client
        self.suppress_notify = True

    async def setup_backgrounds(self):
        await self.client.wait_until_ready()
        self.task_sync_contacts = self.client.loop.create_task(self.sync_contacts())
        self.task_bot_status = self.client.loop.create_task(self.bot_status())
        self.task_discordbots_api = self.client.loop.create_task(self.discordbots_api())
        self.task_mem = self.client.loop.create_task(self.mem_profiler())

    async def __helper_update_contacts_channels(self):
        lg = InsightLogger.InsightLogger.get_logger('Tokens', 'Tokens.log')
        st = InsightLogger.InsightLogger.time_start()
        async for channel in self.client.channel_manager.get_all_channels():
            try:
                await channel.background_contact_sync(message=None, suppress=self.suppress_notify)
            except Exception as ex:
                print(ex)
        self.suppress_notify = False
        InsightLogger.InsightLogger.time_log(lg, st, "Update/reload channels", seconds=True)

    async def sync_contacts(self):
        while True:
            if self.client.service.cli_args.defer_tasks:  # run later
                next_run = 10800 - (time.time() % 10800)  # get time to next 3 hour interval
                next_run = next_run if next_run >= 3600 else 7200
                await asyncio.sleep(next_run)
            try:
                lg = InsightLogger.InsightLogger.get_logger('Tokens', 'Tokens.log')
                st = InsightLogger.InsightLogger.time_start()
                await self.client.loop.run_in_executor(None, partial(tb_tokens.mass_sync_all, self.client.service))
                await self.client.loop.run_in_executor(None, partial(tb_tokens.delete_noTracking, self.client.service))
                await self.__helper_update_contacts_channels()
                InsightLogger.InsightLogger.time_log(lg, st, "Total sync contacts task.", seconds=True)
            except Exception as ex:
                print(ex)
            if not self.client.service.cli_args.defer_tasks:  # run startup
                next_run = 10800 - (time.time() % 10800)  # get time to next 3 hour interval
                next_run = next_run if next_run >= 3600 else 7200
                await asyncio.sleep(next_run)

    async def bot_status(self):
        await self.client.wait_until_ready()
        lg = InsightLogger.InsightLogger.get_logger('Insight.status', 'Insight_status.log')
        while True:
            try:
                update = await self.client.loop.run_in_executor(None, self.client.service.update_available)
                if update:
                    status_str = 'Update available. See console. '
                else:
                    status_str = 'CPU:{}% MEM:{:.1f}GB {} Feeds: {} [Stats 5m] '.format(str(int(psutil.cpu_percent())),
                                                                                       psutil.virtual_memory()[3] / 2. ** 30,
                                                                                       str(self.client.service.get_version()),
                                                                                       self.client.channel_manager.feed_count())
                stats_zk = await self.client.loop.run_in_executor(None, self.client.service.zk_obj.get_stats)
                d_status = discord.Status.online
                if stats_zk[0] <= 10:
                    d_status = discord.Status.idle
                status_str += '[zK] Add: {}, Delay: {}m(+{}s) '.format(stats_zk[0], stats_zk[1], stats_zk[2])
                stats_feeds = await self.client.channel_manager.avg_delay()
                if stats_feeds[1] >= 10:
                    d_status = discord.Status.dnd
                status_str += '[Insight] Sent: {}, Delay: {}s '.format(str(stats_feeds[0]),
                                                                       str(stats_feeds[1]))
                game_act = discord.Activity(name=status_str, type=discord.ActivityType.watching)
                await self.client.change_presence(activity=game_act, status=d_status)
                lg.info(status_str)
            except Exception as ex:
                print(ex)
            next_run = 300 - (time.time() % 300)  # get time to next 5 minute interval
            next_run = next_run if next_run >= 100 else 200
            await asyncio.sleep(next_run)

    async def discordbots_api(self):
        await self.client.wait_until_ready()
        api_token = self.client.service.config_file.get("discordbots.org", "discordbots_apikey", fallback=None)
        db_url = "https://discordbots.org/api/bots/{}/stats".format(str(self.client.user.id))
        db_headers = {"Content-Type": "application/json", "Authorization": str(api_token), **self.client.service.get_headers()}
        if api_token:
            async with aiohttp.ClientSession(headers=db_headers) as client:
                while True:
                    try:
                        payload = {"server_count": len(self.client.guilds)}
                        async with client.post(url=db_url, data=json.dumps(payload), timeout=45) as r:
                            if r.status == 200:
                                pass
                            elif r.status == 401:
                                print('Error 401 for DiscordBots API. DiscordBots posting will now stop.')
                                break
                            else:
                                print('Error: {} - when posting to DiscordBots API'.format(r.status))
                    except asyncio.TimeoutError:
                        print('DiscordBots API timeout.')
                    except Exception as ex:
                        print(ex)
                        traceback.print_exc()
                    await asyncio.sleep(900)

    async def mem_profiler(self):
        await self.client.wait_until_ready()
        mem_tracker = InsightUtilities.MemTracker()
        while True:
            await self.client.loop.run_in_executor(None, mem_tracker.log_summary)
            await asyncio.sleep(3600)


import discord_bot
from database.db_tables import tb_tokens
