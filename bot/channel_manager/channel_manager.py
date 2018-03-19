import asyncio

import bot.discord_bot
from bot.channel_manager.channel import d_channel


class channel_manager(object):
    def __init__(self, con, cf_info, args, discord_client):
        if not isinstance(discord_client, bot.discord_bot.D_client):
            exit()

        print("Started channel manager")

        self.con_ = con
        self.config_file = cf_info
        self.arguments = args
        self.client = discord_client

        self.connected_channels = []

        self.client.loop.create_task(self.channelLoader())

    async def channelLoader(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            for server in self.client.guilds:
                for channel in server.text_channels:
                    if not self.in_connected_channel(channel):
                        self.connected_channels.append(
                            d_channel(channel_manager_instance=self, channel_instance=channel))
            await asyncio.sleep(60)

    def in_connected_channel(self, new_channel):
        for i in self.connected_channels:
            if i.channel.id == new_channel.id:
                return True
        return False

    def return_channel(self, channel_lookup):
        for i in self.connected_channels:
            if i.channel.id == channel_lookup.id:
                return i
        return None

    async def command_to_channel(self, message):
        channel_tmp = self.return_channel(message.channel)
        if channel_tmp is not None:
            await channel_tmp.listen_command(message)
        else:
            await message.channel.send("This channel is not loaded or permissions are incorrect. Please wait 60 seconds"
                                       " and try again if you just recently invited the bot to this "
                                       "channel. \n\nNote: You are"
                                       " unable to create feeds in private conversations or group chats "
                                       "as these features"
                                       " are only supported by channels within Discord servers.\n")
