from .FiltersVisualsEmbedded import *


class visual_capradar(base_visual):

    def __init__(self, km_row, discord_channel_object, overall_filters, feed_specific_row):
        super(visual_capradar, self).__init__(km_row, discord_channel_object, overall_filters, feed_specific_row)
        assert isinstance(self.feed_options, tb_capRadar)

    def set_links_images(self):
        self.__zk_kill = "https://zkillboard.com/kill/{}/".format(str(self.km.kill_id))
        pass

    def internal_list_options(self):
        super(visual_capradar, self).internal_list_options()
        self.in_attackers_affiliation = internal_options.use_blacklist.value
        self.in_attackers_ship_group = internal_options.use_whitelist.value

    def __make_vars(self):
        __zk_pilot = "https://zkillboard.com/character/{}/"
        pass

    def __make_header(self):
        pass

    def __make_body(self):
        pass

    def generate_view(self):
        self.__make_vars()
        self.__make_header()
        self.__make_body()

    def run_filter(self):
       return False

    @classmethod
    def feed_specific_row_type(cls):
        return tb_capRadar