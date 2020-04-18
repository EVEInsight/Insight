from InsightUtilities.InsightSingleton import InsightSingleton
from InsightUtilities.ConfigLoader import ConfigLoader
from InsightUtilities.LimitSystem.LimitClient import LimitClient, LimitClientHP
import asyncio
import discord
import InsightExc
import traceback


class LimitManager(metaclass=InsightSingleton):
    def __init__(self):
        self.config: ConfigLoader = ConfigLoader()
        self.loop = asyncio.get_event_loop()
        self.limit_global = self.config.get("LIMITER_GLOBAL_TICKETS")
        self.interval_global = self.config.get("LIMITER_GLOBAL_INTERVAL")
        self.limit_dm = self.config.get("LIMITER_DM_TICKETS")
        self.interval_dm = self.config.get("LIMITER_DM_INTERVAL")
        self.limit_user = self.config.get("LIMITER_USER_TICKETS")
        self.interval_user = self.config.get("LIMITER_USER_INTERVAL")
        self.limit_guild = self.config.get("LIMITER_GUILD_TICKETS")
        self.interval_guild = self.config.get("LIMITER_GUILD_INTERVAL")
        self.limit_channel = self.config.get("LIMITER_CHANNEL_TICKETS")
        self.interval_channel = self.config.get("LIMITER_CHANNEL_INTERVAL")
        self.limiter_global = LimitClient(None, self.limit_global, self.interval_global, "Global", True)
        self.limiter_dm = LimitClient(self.limiter_global, self.limit_dm, self.interval_dm, "Global DM", True)
        self.servers = {}
        self.channels = {}
        self.users = {}
        self.lock = asyncio.Lock(loop=self.loop)

    def get_guild_limiter(self, discord_guild_object: discord.Guild) -> LimitClient:
        limiter = self.servers.get(discord_guild_object.id)
        if not limiter:
            limiter = LimitClient(self.limiter_global, self.limit_guild, self.interval_guild, discord_guild_object.name)
            self.servers[discord_guild_object.id] = limiter
        return limiter

    def get_channel_limiter(self, discord_channel_object: discord.TextChannel) -> LimitClient:
        limiter = self.channels.get(discord_channel_object.id)
        if not limiter:
            limiter = LimitClient(self.get_guild_limiter(discord_channel_object.guild),
                                  self.limit_channel, self.interval_channel, discord_channel_object.name)
            self.channels[discord_channel_object.id] = limiter
        return limiter

    def get_user_limiter(self, discord_user_object: discord.User):
        limiter = self.users.get(discord_user_object.id)
        if not limiter:
            limiter = LimitClient(self.limiter_dm, self.limit_user, self.interval_user, discord_user_object.name)
            self.users[discord_user_object.id] = limiter
        return limiter

    async def get_cm(self, discord_object):
        async with self.lock:
            if isinstance(discord_object, discord.Message):
                if isinstance(discord_object.channel, discord.DMChannel):
                    return self.get_user_limiter(discord_object.author)
                elif isinstance(discord_object.channel, discord.TextChannel):
                    return self.get_channel_limiter(discord_object.channel)
                else:
                    traceback.print_stack()
                    raise InsightExc.userInput.InsightProgrammingError("Unknown object type when getting limit manager.")
            elif isinstance(discord_object, discord.TextChannel):
                return self.get_channel_limiter(discord_object)
            elif isinstance(discord_object, discord.DMChannel):
                return self.get_user_limiter(discord_object.recipient)
            else:
                print("Unknown object type when getting limit manager. {}".format(type(discord_object)))
                raise InsightExc.userInput.InsightProgrammingError("Unknown object type when getting limit manager.")

    @classmethod
    async def cm(cls, discord_object) -> LimitClient:
        lm = LimitManager()
        return await lm.get_cm(discord_object)

    @classmethod
    async def cm_hp(cls, discord_object) -> LimitClient:
        """"High priority context manager"""
        lm = LimitManager()
        return LimitClientHP(await lm.get_cm(discord_object))
