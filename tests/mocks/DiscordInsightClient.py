from discord_bot import discord_main
import asyncio


class DiscordInsightClient(discord_main.Discord_Insight_Client):
    def __init__(self):
        return

    @property
    def loop(self):
        return asyncio.get_event_loop()
