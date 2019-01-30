import discord
from tests.mocks.libDiscord.Guild import Guild
from tests.mocks.EmulatedService import MessageSendReceive


class TextChannel(discord.TextChannel):
    def __init__(self, channel_id, gulid_id, guild_obj=None):
        self.id = channel_id
        self.guild_id = gulid_id
        self.guild_object = guild_obj

    @property
    def guild(self):
        return self.guild_object if self.guild_object is not None else Guild(self.guild_id)

    def permissions_for(self, member):
        return discord.Permissions()

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        if content:
            MessageSendReceive.MessageSendReceive().send_message(content)
        elif embed:
            MessageSendReceive.MessageSendReceive().send_message(embed)
        else:
            raise ValueError
