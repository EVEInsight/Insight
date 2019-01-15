import discord
from tests.mocks.libDiscord.Guild import Guild


class TextChannel(discord.TextChannel):
    def __init__(self, channel_id, gulid_id, guild_obj=None):
        self.id = channel_id
        self.guild_id = gulid_id
        self.guild_object = guild_obj

    @property
    def guild(self):
        return self.guild_object if self.guild_object is not None else Guild(self.guild_id)

