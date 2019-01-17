import discord


class User(discord.User):
    def __init__(self, user_id=None, name=None):
        self.id = user_id
        self.name = name

    @property
    def mention(self):
        return "@{}".format(self.name)
