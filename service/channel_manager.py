import discord_bot
import random
import discord_bot.channel_types as cType
from functools import partial
import discord
import asyncio
import datetime


class Channel_manager(object):
    def __init__(self, serivce_module):
        self.service = serivce_module
        self.__channel_feed_container = {}
        self.__dm_container = {}
        self.__discord_client:discord_bot.Discord_Insight_Client = None
        self.__km_post_delays = asyncio.Queue()

    async def add_delay(self, seconds_number):
        try:
            self.__km_post_delays.put_nowait(seconds_number)
        except Exception as ex:
            print(ex)

    async def avg_delay(self):
        values = []
        total = 0
        avg = 0
        try:
            while True:
                values.append(self.__km_post_delays.get_nowait())
        except asyncio.QueueEmpty:
            try:
                total = len(values)
                avg = sum(values) / total
            except:
                pass
        except Exception as ex:
            print(ex)
        finally:
            return (total, round(avg, 1))

    def get_discord_client(self):
        assert isinstance(self.__discord_client,discord_bot.Discord_Insight_Client)
        return self.__discord_client

    def __get_active_channels(self):
        __feeds = list(self.__channel_feed_container.values())
        random.shuffle(__feeds)
        return __feeds

    def sy_get_all_channels(self):
        for channel in self.__get_active_channels():
            yield channel

    async def get_all_channels(self):
        for channel in self.__get_active_channels():
            yield channel

    async def get_all_capRadar(self):
        async for channel in self.get_all_channels():
            if isinstance(channel, cType.insight_capRadar):
                yield channel

    async def get_all_enFeed(self):
        async for channel in self.get_all_channels():
            if isinstance(channel, cType.insight_enFeed):
                yield channel

    async def __get_text_channels(self):
        for guild in self.__discord_client.guilds:
            for channel in guild.text_channels:
                yield channel

    async def set_client(self,client_object):
        try:
            assert isinstance(client_object,discord_bot.Discord_Insight_Client)
            self.__discord_client = client_object
        except AssertionError:
            exit(1)

    async def load_channels(self):
        async for i in self.__get_text_channels():
            await self.get_channel_feed(i)

    async def add_feed_object(self,ch_feed_object):
        self.__channel_feed_container[ch_feed_object.channel_id] = ch_feed_object
        return ch_feed_object

    async def __add_channel(self,discord_channel_object,ch_feed_object_type):
        return await self.add_feed_object(await ch_feed_object_type.load_new(discord_channel_object,self.service,self.__discord_client))

    async def __remove_container(self,ch_id_int):
        return self.__channel_feed_container.pop(ch_id_int)

    async def __already_exists(self,ch_id):
        try:
            return await self.__discord_client.loop.run_in_executor(None,partial(cType.insight_textChannel_NoFeed.get_existing_feed_type),ch_id,self.service)
        except Exception as ex:
            print(ex)

    async def get_channel_feed(self,channel_object:discord.TextChannel):
        try:
            assert isinstance(channel_object,discord.TextChannel)
            __feed_obj = self.__channel_feed_container.get(channel_object.id)
            if __feed_obj is not None:
                return __feed_obj
            else:
                __ch_feed_type = await self.__already_exists(channel_object.id)
                if __ch_feed_type is not None:
                    return await self.__add_channel(channel_object,__ch_feed_type)
                else:
                    return cType.insight_textChannel_NoFeed(channel_object, self.service)
        except AssertionError:
            assert isinstance(channel_object,discord.DMChannel)
            return cType.insight_directMessage(channel_object,self.service)

    async def get_user_dm(self, message_object: discord.Message):
        try:
            assert isinstance(message_object, discord.Message)
            await message_object.author.send("Opening a new conversation! Hello!")
            dm = message_object.author.dm_channel
            return cType.insight_directMessage(dm, self.service)
        except Exception as ex:
            print(ex)

    async def remove_feed(self,channel):
        ch_obj = None
        if isinstance(channel,int):
            ch_obj = await self.__remove_container(channel)
        elif isinstance(channel,discord.TextChannel):
            ch_obj = await self.__remove_container(channel.id)
        if ch_obj is not None:
            await ch_obj.remove()

    async def delete_feed(self,channel):
        ch_obj = None
        if isinstance(channel,int):
            ch_obj = await self.__remove_container(channel)
        elif isinstance(channel,discord.TextChannel):
            ch_obj = await self.__remove_container(channel.id)
        if ch_obj is not None:
            if await ch_obj.delete():
                return True
            else:
                return False

    def post_message(self,message_txt):
        for feed in self.sy_get_all_channels():
            try:
                feed.add_message(message_txt)
            except Exception as ex:
                print(ex)

    def send_km(self, km):
        assert isinstance(km, tb_kills)
        for feed in self.sy_get_all_channels():
            try:
                feed.add_km(km)
            except Exception as ex:
                print(ex)

    async def post_all_queued(self):
        while True:
            async for feed in self.get_all_channels():
                try:
                    if feed.deque_done():
                        feed.set_deque_task(self.__discord_client.loop.create_task(feed.post_all()))
                except Exception as ex:
                    print(ex)
            await asyncio.sleep(.1)


from database.db_tables.eve import tb_kills
