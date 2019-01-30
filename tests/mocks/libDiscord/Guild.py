import discord
from tests.mocks.libDiscord import User

class Guild(discord.Guild):
    def __init__(self, guild_id):
        self.id = guild_id

    @property
    def name(self):
        return "test name"

    @property
    def me(self):
        return User.User(None, "TestSuiteBot")
