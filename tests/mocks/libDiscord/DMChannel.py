import discord


class DMChannel(discord.DMChannel):
    def __init__(self, channel_id):
        self.id = channel_id

