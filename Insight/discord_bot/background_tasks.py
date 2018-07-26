import discord
import asyncio
from functools import partial
import psutil
import datetime


class background_tasks(object):
    def __init__(self, insight_client):
        assert isinstance(insight_client, discord_bot.Discord_Insight_Client)
        self.client: discord_bot.Discord_Insight_Client = insight_client

    async def setup_backgrounds(self):
        await self.client.wait_until_ready()
        self.task_sync_contacts = self.client.loop.create_task(self.sync_contacts())
        self.task_bot_status = self.client.loop.create_task(self.bot_status())

    async def __helper_update_contacts_channels(self):
        async for channel in self.client.channel_manager.get_all_capRadar():
            try:
                await channel.sync_settings.InsightOption_syncnow(None)
            except Exception as ex:
                print(ex)

    async def sync_contacts(self):
        while True:
            await asyncio.sleep(5400)  # run every 1.5 hours, run later instead of start
            print("Starting sync contacts task")
            try:
                await self.client.loop.run_in_executor(None, partial(tb_tokens.mass_sync_all, self.client.service))
                await self.__helper_update_contacts_channels()
            except Exception as ex:
                print(ex)

    async def bot_status(self):
        await self.client.wait_until_ready()
        last_warning = datetime.datetime.utcnow() - datetime.timedelta(minutes=175)
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
                if stats_zk[0] == 10 or stats_zk[3] >= 6:
                    d_status = discord.Status.idle
                if stats_zk[2] > 100:
                    stats_zk[2] = "99+"
                status_str += '[zK] Add: {}, AVG Delay: {}m(+{}s), AVG Next: {}s '.format(
                    str(stats_zk[0]), str(stats_zk[1]), str(stats_zk[2]), str(stats_zk[3]))
                stats_feeds = await self.client.channel_manager.avg_delay()
                if stats_feeds[1] >= 30:
                    d_status = discord.Status.dnd
                    if datetime.datetime.utcnow() >= last_warning + datetime.timedelta(hours=3):
                        msg = "Service Warning: \nThe average Insight filtering and posting task delay is {} seconds. This " \
                              "indicates service issues with Discord or the Insight bot could be under heavy load.".format(
                            stats_feeds[1])
                        await self.client.loop.run_in_executor(None,
                                                               partial(self.client.channel_manager.post_message, msg))
                        last_warning = datetime.datetime.utcnow()
                status_str += '[Insight] Sent: {}, AVG Delay: {}s '.format(str(stats_feeds[0]),
                                                                           str(stats_feeds[1]))
                game_act = discord.Activity(name=status_str, type=discord.ActivityType.watching)
                await self.client.change_presence(activity=game_act, status=d_status)
            except Exception as ex:
                print(ex)
            await asyncio.sleep(300)


import discord_bot
from database.db_tables import tb_tokens
