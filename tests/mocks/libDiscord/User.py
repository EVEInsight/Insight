import discord


class User(discord.User):
    def __init__(self, user_id=None, name=None, manager_server=False):
        self.id = user_id
        self.name = name
        if manager_server:
            self._permissions = discord.Permissions.all_channel()
        else:
            self._permissions = discord.Permissions(permissions=0)

    @property
    def mention(self):
        return "@{}".format(self.name)


    def permissions_in(self, channel):
        return self._permissions
