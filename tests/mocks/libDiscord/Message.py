import discord
import random


class Message(discord.Message):
    def __init__(self, channel, user, content):
        self.id = random.randint(0, 100)
        self.channel = channel
        self.user = user
        self.content = content

    @property
    def author(self):
        return self.user

    def __str__(self):
        return self.content



