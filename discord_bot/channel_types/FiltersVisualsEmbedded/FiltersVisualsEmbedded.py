import discord
import enum


class internal_options(enum.Enum):
    use_blacklist = True
    use_whitelist = False


class base_visual(object):
    def __init__(self,km_row,discord_channel_object,overall_filters,feed_specific_row):
        assert isinstance(km_row,tb_kills)
        assert isinstance(discord_channel_object,discord.TextChannel)
        assert isinstance(overall_filters,tb_channels)
        assert isinstance(feed_specific_row,self.feed_specific_row_type())
        self.kn = km_row
        self.channel = discord_channel_object
        self.filters = overall_filters
        self.feed_options = feed_specific_row
        self.__internal_list_options()

    def __internal_list_options(self):
        self.__attackers_affiliation = internal_options.use_blacklist.value
        self.__attackers_ship_group = internal_options.use_whitelist.value

    def __run_filter(self):
        pass

    def __bool__(self):
        pass

    async def __call__(self, *args, **kwargs):
        await self.channel.send("")

    @classmethod
    def feed_specific_row_type(cls):
        raise NotImplementedError
        #return tb_enfeed  <example

from database.db_tables import *