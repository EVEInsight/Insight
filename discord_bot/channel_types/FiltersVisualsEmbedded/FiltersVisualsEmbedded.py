import enum
from abc import ABCMeta, abstractmethod


class internal_options(enum.Enum):
    use_blacklist = True
    use_whitelist = False


class base_visual(metaclass=ABCMeta):
    def __init__(self,km_row,discord_channel_object,overall_filters,feed_specific_row):
        assert isinstance(km_row,tb_kills)
        assert isinstance(discord_channel_object,discord.TextChannel)
        assert isinstance(overall_filters,tb_channels)
        assert isinstance(feed_specific_row,self.feed_specific_row_type())
        self.km = km_row
        self.channel = discord_channel_object
        self.filters = overall_filters
        self.feed_options = feed_specific_row
        self.internal_list_options()
        self.embed = discord.Embed()
        self.set_links_images()

    @abstractmethod
    def internal_list_options(self):
        self.in_attackers_affiliation = internal_options.use_blacklist.value
        self.in_attackers_ships_type = internal_options.use_blacklist.value
        self.in_attackers_ship_group = internal_options.use_blacklist.value
        self.in_attackers_ships_category = internal_options.use_blacklist.value
        self.in_victim_affiliation = internal_options.use_blacklist.value
        self.in_victim_ship_type = internal_options.use_blacklist.value
        self.in_victim_ship_group = internal_options.use_blacklist.value
        self.in_victim_ship_category = internal_options.use_blacklist.value

    def set_links_images(self):
        raise NotImplementedError

    def run_filter(self):
        pass

    def generate_view(self):
        raise NotImplementedError

    def __bool__(self):
        try:
            __resp = self.run_filter()
            assert isinstance(__resp,bool)
            if __resp:
                self.generate_view()
            return __resp
        except Exception as ex:
            print(ex)
            return False

    async def __call__(self, *args, **kwargs):
        await self.channel.send(content="", embed=self.embed)

    @abstractmethod
    def feed_specific_row_type(cls):
        raise NotImplementedError
        #return tb_enfeed  <example

from database.db_tables import *
import discord