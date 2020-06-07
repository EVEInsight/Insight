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
                next_run = 21600 - (time.time() % 21600)  # get time to next 6 hour interval
                next_run = next_run if next_run >= 7200 else 14400
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
                next_run = 21600 - (time.time() % 21600)  # get time to next 6 hour interval
                next_run = next_run if next_run >= 7200 else 14400
                await asyncio.sleep(next_run)

    async def discordbots_api(self):
        await self.client.wait_until_ready()
        api_token = self.client.service.config.get("DISCORDBOTS_APIKEY")
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
