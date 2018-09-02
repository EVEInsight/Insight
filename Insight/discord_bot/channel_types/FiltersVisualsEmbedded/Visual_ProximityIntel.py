from .VisualCapRadarFunctional import *


class Visual_ProximityIntel(VisualCapRadarFunctional):
    def internal_list_options(self):
        super(visual_capradar, self).internal_list_options()
        self.in_attackers_affiliation = internal_options.use_blacklist.value
        self.in_attackers_ship_group = internal_options.use_whitelist.value
        self.in_system_nonly = internal_options.use_whitelist.value

    def make_links(self):
        super(visual_capradar, self).make_links()

    def make_images(self):
        super(visual_capradar, self).make_images()

    def make_vars(self):
        super(visual_capradar, self).make_vars()

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
        list_sys_reg = self.filters.object_filter_systems + self.filters.object_filter_regions
        if not self.km.filter_system(list_sys_reg, self.in_system_nonly):
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

    @classmethod
    def appearance_id(cls):
        return super(visual_capradar, cls).appearance_id()

    @classmethod
    def appearance_options(cls):
        yield cls

    @classmethod
    def get_desc(cls):
        return "Utility - Null"
