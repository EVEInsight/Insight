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

        self.limit_global_sustain = self.config.get("LIMITER_GLOBAL_SUSTAIN_TICKETS")
        self.interval_global_sustain = self.config.get("LIMITER_GLOBAL_SUSTAIN_INTERVAL")
        self.limit_global_burst = self.config.get("LIMITER_GLOBAL_BURST_TICKETS")
        self.interval_global_burst = self.config.get("LIMITER_GLOBAL_BURST_INTERVAL")

        self.limit_dm_sustain = self.config.get("LIMITER_DM_SUSTAIN_TICKETS")
        self.interval_dm_sustain = self.config.get("LIMITER_DM_SUSTAIN_INTERVAL")
        self.limit_dm_burst = self.config.get("LIMITER_DM_BURST_TICKETS")
        self.interval_dm_burst = self.config.get("LIMITER_DM_BURST_INTERVAL")

        self.limit_user_sustain = self.config.get("LIMITER_USER_SUSTAIN_TICKETS")
        self.interval_user_sustain = self.config.get("LIMITER_USER_SUSTAIN_INTERVAL")
        self.limit_user_burst = self.config.get("LIMITER_USER_BURST_TICKETS")
        self.interval_user_burst = self.config.get("LIMITER_USER_BURST_INTERVAL")

        self.limit_guild_sustain = self.config.get("LIMITER_GUILD_SUSTAIN_TICKETS")
        self.interval_guild_sustain = self.config.get("LIMITER_GUILD_SUSTAIN_INTERVAL")
        self.limit_guild_burst = self.config.get("LIMITER_GUILD_BURST_TICKETS")
        self.interval_guild_burst = self.config.get("LIMITER_GUILD_BURST_INTERVAL")

        self.limit_channel_sustain = self.config.get("LIMITER_CHANNEL_SUSTAIN_TICKETS")
        self.interval_channel_sustain = self.config.get("LIMITER_CHANNEL_SUSTAIN_INTERVAL")
        self.limit_channel_burst = self.config.get("LIMITER_CHANNEL_BURST_TICKETS")
        self.interval_channel_burst = self.config.get("LIMITER_CHANNEL_BURST_INTERVAL")

        self.limiter_global_sustain = LimitClient(None, self.limit_global_sustain, self.interval_global_sustain,
                                                  "Global (Sustain)", True)
        self.limiter_global_burst = LimitClient(self.limiter_global_sustain, self.limit_global_burst,
                                                self.interval_global_burst, "Global (Burst)", True)
        self.limiter_dm_sustain = LimitClient(self.limiter_global_burst, self.limit_dm_sustain,
                                              self.interval_dm_sustain, "Global DM (Sustain)", True)
        self.limiter_dm_burst = LimitClient(self.limiter_dm_sustain, self.limit_dm_burst, self.interval_dm_burst,
                                            "Global DM (Burst)", True)
        self.servers_sustain = {}
        self.servers_burst = {}
        self.channels_sustain = {}
        self.channels_burst = {}
        self.users_sustain = {}
        self.users_burst = {}

        self.lock = asyncio.Lock(loop=self.loop)

    def get_guild_limiter(self, discord_guild_object: discord.Guild) -> LimitClient:
        limiter_burst = self.servers_burst.get(discord_guild_object.id)
        if not limiter_burst:
            sustain_name = "{} [{}] (Sustain)".format(discord_guild_object.name, discord_guild_object.id)
            burst_name = "{} [{}] (Burst)".format(discord_guild_object.name, discord_guild_object.id)
            limiter_sustain = LimitClient(self.limiter_global_burst, self.limit_guild_sustain,
                                          self.interval_guild_sustain, sustain_name)
            limiter_burst = LimitClient(limiter_sustain, self.limit_guild_burst, self.interval_guild_burst, burst_name)
            self.servers_sustain[discord_guild_object.id] = limiter_sustain
            self.servers_burst[discord_guild_object.id] = limiter_burst
        return limiter_burst

    def get_channel_limiter(self, discord_channel_object: discord.TextChannel) -> LimitClient:
        limiter_burst = self.channels_burst.get(discord_channel_object.id)
        if not limiter_burst:
            sustain_name = "{} [{}] (Sustain)".format(discord_channel_object.name, discord_channel_object.id)
            burst_name = "{} [{}] (Burst)".format(discord_channel_object.name, discord_channel_object.id)
            limiter_sustain = LimitClient(self.get_guild_limiter(discord_channel_object.guild),
                                          self.limit_channel_sustain, self.interval_channel_sustain, sustain_name)
            limiter_burst = LimitClient(limiter_sustain, self.limit_channel_burst,
                                        self.interval_channel_burst, burst_name)
            self.channels_sustain[discord_channel_object.id] = limiter_sustain
            self.channels_burst[discord_channel_object.id] = limiter_burst
        return limiter_burst

    def get_user_limiter(self, discord_user_object: discord.User):
        limiter_burst = self.users_burst.get(discord_user_object.id)
        if not limiter_burst:
            sustain_name = "{} [{}] (Sustain)".format(discord_user_object.name, discord_user_object.id)
            burst_name = "{} [{}] (Burst)".format(discord_user_object.name, discord_user_object.id)
            limiter_sustain = LimitClient(self.limiter_dm_burst, self.limit_user_sustain, self.interval_user_sustain,
                                          sustain_name)
            limiter_burst = LimitClient(limiter_sustain, self.limit_user_burst, self.interval_user_burst, burst_name)
            self.users_sustain[discord_user_object.id] = limiter_sustain
            self.users_burst[discord_user_object.id] = limiter_burst
        return limiter_burst

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
