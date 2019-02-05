import discord
from tests.mocks.libDiscord import User
from tests.mocks.EmulatedService import MessageSendReceive


class DMChannel(discord.DMChannel):
    def __init__(self, channel_id):
        self.id = channel_id
        self.recipient = User.User(1)

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        if content:
            MessageSendReceive.MessageSendReceive().send_message(content)
        elif embed:
            MessageSendReceive.MessageSendReceive().send_message(embed)
        else:
            raise ValueError

