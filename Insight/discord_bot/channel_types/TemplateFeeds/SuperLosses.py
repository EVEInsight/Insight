from ..enFeed import *


class VisualSuperLosses(visual_enfeed):
    def internal_list_options(self):
        super(visual_enfeed, self).internal_list_options()
        self.in_victim_ship_group = internal_options.use_whitelist.value

    def set_frame_color(self):
        self.embed.color = discord.Color(2640791)


class SuperLosses(enFeed):
    def get_linked_options(self):
        return Linked_Options.opt_basicfeed(self)

    def linked_visual(self, km_row):
        return VisualSuperLosses(km_row, self.channel_discord_object, self.cached_feed_table, self.cached_feed_specific)

    @classmethod
    def get_template_id(cls):
        return 1

    @classmethod
    def get_template_desc(cls):
        return "SuperLosses - Displays only super losses"

    def __str__(self):
        return "SuperLosses Feed"
