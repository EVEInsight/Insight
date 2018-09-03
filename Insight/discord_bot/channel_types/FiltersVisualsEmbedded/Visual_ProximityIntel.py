from .FiltersVisualsEmbedded import *


class Visual_ProximityIntel(base_visual):
    def __init__(self, km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object):
        super().__init__(km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object)
        self.tracked_hostiles = []

    def internal_list_options(self):
        super().internal_list_options()
        self.in_attackers_affiliation = internal_options.use_blacklist.value
        self.in_system_nonly = internal_options.use_whitelist.value

    def make_links(self):
        super().make_links()

    def make_images(self):
        super().make_images()

    def make_vars(self):
        super().make_vars()

    def make_text_heading(self):
        pass

    def make_header(self):
        self.text_only = True
        self.message_txt = "{} {}".format(self.mention_method(), self.zk_kill)

    def make_body(self):
        pass

    def run_filter(self):
        tdiff = datetime.datetime.utcnow() - datetime.timedelta(minutes=self.feed_options.max_km_age)
        if tdiff >= self.km.killmail_time:
            return False
        list_sys_reg = self.filters.object_filter_systems + self.filters.object_filter_constellations + self.filters.object_filter_regions
        self.base_sysConstReg = self.km.filter_system(list_sys_reg, self.in_system_nonly)
        if self.base_sysConstReg is None:
            # todo check gate jump distance if fail
            return False
        list_typeGroup = self.filters.object_filter_groups + self.filters.object_filter_types
        tracked_ships = self.km.filter_attackers(self.km.object_attackers, list_typeGroup, self.in_attackers_ship_group)
        if len(tracked_ships) == 0:
            return False
        list_aff = self.filters.object_filter_alliances + self.filters.object_filter_corporations + self.filters.object_filter_characters
        self.tracked_hostiles = self.km.filter_attackers(tracked_ships, list_aff, self.in_attackers_affiliation)
        if len(self.tracked_hostiles) == 0:
            return False
        return True

    def set_frame_color(self):
        s = (datetime.datetime.utcnow() - self.km.killmail_time).total_seconds()
        if 0 <= s <= 60:
            self.color = discord.Color(12124259)
        elif 60 <= s <= 300:
            self.color = discord.Color(8454210)
        else:
            self.color = discord.Color(4128800)
        super().set_frame_color()

    @classmethod
    def feed_specific_row_type(cls):
        return tb_capRadar

    @classmethod
    def appearance_options(cls):
        yield cls

    @classmethod
    def get_desc(cls):
        return "Utility - Null"
