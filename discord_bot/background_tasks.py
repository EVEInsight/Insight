import discord
import asyncio
from functools import partial


class background_tasks(object):
    def __init__(self, insight_client):
        assert isinstance(insight_client, discord_bot.Discord_Insight_Client)
        self.client: discord_bot.Discord_Insight_Client = insight_client

    async def setup_backgrounds(self):
        await self.client.wait_until_ready()
        self.task_sync_contacts = self.client.loop.create_task(self.sync_contacts())

    async def __helper_update_contacts_channels(self):
        async for channel in self.client.channel_manager.get_all_channels():
            if isinstance(channel, discord_bot.channel_types.insight_capRadar):
                try:
                    await channel.sync_settings.InsightOption_syncnow(None)
                except Exception as ex:
                    print(ex)

    async def sync_contacts(self):
        while True:
            print("Running sync contacts task")
            try:
                await self.client.loop.run_in_executor(None, partial(tb_tokens.mass_sync_all, self.client.service))
                await self.__helper_update_contacts_channels()
            except Exception as ex:
                print(ex)
            await asyncio.sleep(25200)  # run every 7 hours


import discord_bot
from database.db_tables import tb_tokens
