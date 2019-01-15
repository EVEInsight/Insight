import discord


class Guild(discord.Guild):
    def __init__(self, guild_id):
        self.id = guild_id
