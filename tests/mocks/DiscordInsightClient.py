from discord_bot import discord_main
from tests.mocks.libDiscord.User import User
import asyncio
from tests.mocks.EmulatedService.MessageSendReceive import MessageSendReceive


class DiscordInsightClient(discord_main.Discord_Insight_Client):
    def __init__(self):
        self.channels = []

    @property
    def loop(self):
        return asyncio.get_event_loop()

    def add_channel(self, channel):
        self.channels.append(channel)

    def get_all_channels(self):
        return self.channels

    @property
    def user(self):
        return User(1, "Insight")

    def wait_for(self, event, *, check=None, timeout=None):
        f = asyncio.ensure_future(MessageSendReceive().wait_for_message())
        return asyncio.wait_for(f, timeout, loop=self.loop)
