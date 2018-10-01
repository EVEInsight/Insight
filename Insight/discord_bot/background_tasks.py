import discord
import asyncio
from functools import partial
import psutil
import datetime
import requests
import json
import aiohttp
import traceback


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

    async def __helper_update_contacts_channels(self):
        async for channel in self.client.channel_manager.get_all_channels():
            try:
                await channel.background_contact_sync(message=None, suppress=self.suppress_notify)
            except Exception as ex:
                print(ex)
        self.suppress_notify = False

    async def sync_contacts(self):
        while True:
            if self.client.service.cli_args.defer_tasks:
                await asyncio.sleep(5400)  # run every 1.5 hours, run later instead of start
            try:
                await self.client.loop.run_in_executor(None, partial(tb_tokens.mass_sync_all, self.client.service))
                await self.client.loop.run_in_executor(None, partial(tb_tokens.delete_noTracking, self.client.service))
                await self.__helper_update_contacts_channels()
            except Exception as ex:
                print(ex)
            if not self.client.service.cli_args.defer_tasks:
                await asyncio.sleep(5400)  # run every 1.5 hours

    async def bot_status(self):
        await self.client.wait_until_ready()
        while True:
            try:
                update = await self.client.loop.run_in_executor(None, self.client.service.update_available)
                if update:
                    status_str = 'Update available. See console. '
                else:
                    status_str = 'CPU:{}% MEM:{:.1f}GB {} [Stats 5m] '.format(str(int(psutil.cpu_percent())),
                                                                              psutil.virtual_memory()[3] / 2. ** 30,
                                                                              str(self.client.service.get_version()))
                stats_zk = await self.client.loop.run_in_executor(None, self.client.service.zk_obj.get_stats)
                d_status = discord.Status.online
                if stats_zk[0] <= 10:
                    d_status = discord.Status.idle
                status_str += '[zK] Add: {}, Delay: {}m(+{}s), Next: {}s '.format(
                    str(stats_zk[0]), str(stats_zk[1]), str(stats_zk[2]), str(stats_zk[3]))
                stats_feeds = await self.client.channel_manager.avg_delay()
                if stats_feeds[1] >= 10:
                    d_status = discord.Status.dnd
                status_str += '[Insight] Sent: {}, Delay: {}s '.format(str(stats_feeds[0]),
                                                                       str(stats_feeds[1]))
                game_act = discord.Activity(name=status_str, type=discord.ActivityType.watching)
                await self.client.change_presence(activity=game_act, status=d_status)
            except Exception as ex:
                print(ex)
            await asyncio.sleep(300)

    async def discordbots_api(self):
        await self.client.wait_until_ready()
        api_token = self.client.service.config_file.get("discordbots.org", "discordbots_apikey", fallback=None)
        db_url = "https://discordbots.org/api/bots/{}/stats".format(str(self.client.user.id))
        db_headers = {"Content-Type": "application/json", "Authorization": str(api_token),
                   "User-Agent": "InsightDiscordKillfeeds"}
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


import discord_bot
from database.db_tables import tb_tokens
