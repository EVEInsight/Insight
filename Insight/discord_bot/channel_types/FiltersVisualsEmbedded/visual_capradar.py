from .FiltersVisualsEmbedded import *


class visual_capradar(base_visual):
    def __init__(self, km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object):
        super().__init__(km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object)
        self.tracked_hostiles = []
        self.baseSystem: tb_systems = None

    def internal_list_options(self):
        super(visual_capradar, self).internal_list_options()
        self.in_attackers_affiliation = internal_options.use_blacklist.value
        self.in_attackers_ship_group = internal_options.use_whitelist.value
        self.in_system_ly = internal_options.use_whitelist.value

    def make_vars(self):
        super().make_vars()
        self.hv: tb_attackers = self.km.get_highest_attacker(self.tracked_hostiles)

    def extract_mention(self):
        global_mention = super().extract_mention()
        if global_mention != enum_mention.noMention:
            return global_mention
        assert isinstance(self.hv, tb_attackers)
        for c in self.list_typeGroup:
            if self.hv.compare_filter_list(c):
                return c.mention
        return enum_mention.noMention

    def make_text_heading(self):
        overview_text = "{haAfi} {haS} activity in {sysReg}".format(haAfi=self.hv.str_highest_name(), haS=self.hv.str_shipGroup_name(), sysReg=str(self.system))
        self.message_txt = "{} {} {}".format(self.mention_method(), overview_text, self.km.str_minutes_ago())

    def make_header(self):
        overview_text = "{haS} activity in {sysReg} {ly} LYs from {bSys}".format(haS=self.hv.str_ship_name(), sysReg=str(self.system), ly=self.km.str_ly_range(self.baseSystem), bSys=self.baseSystem.str_system_name())
        self.embed.set_author(name=overview_text, icon_url=self.hv.str_highest_image(64), url=self.km.str_zk_link())
        e_desc = '**{vS}** destroyed in **[{sysN}]' \
                 '({sysL})**({rgN}) {mAgo}{loc}\n\n' \
                 '*Involving **[{haP}]({haP_l})({haAfi})** in a **{haS}** {inv}.*' \
            .format(vS=self.vi.str_ship_name(), sysN=self.system.str_system_name(), sysL=self.system.str_dotlan_map(),
                    rgN=self.system.str_region_name(), mAgo=self.km.str_minutes_ago(True),
                    loc=self.km.str_location_name(), haP=self.hv.str_pilot_name(), haP_l=self.hv.str_pilot_zk(),
                    haAfi=self.hv.str_highest_name(), haS=self.hv.str_ship_name(), inv=self.km.str_attacker_count())
        self.embed.description = e_desc
        self.embed.title = " "
        self.embed.set_thumbnail(url=self.hv.str_ship_image(128))

    def make_body(self):
        heading = "**{} of {} attackers flying in tracked ships**".format(str(len(self.tracked_hostiles)),
                                                                          self.km.str_total_involved())
        body = "```{}```".format(self.km.str_overview(self.tracked_hostiles), zk=self.km.str_zk_link())
        self.embed.add_field(name=heading, value=body, inline=False)
        heading_routes = "Dotlan routes from {}".format(self.baseSystem.str_system_name())
        self.embed.add_field(name=heading_routes, value=self.helper_routes(), inline=False)

    def make_footer(self):
        self.embed.set_footer(text="{ly} LY/{j} J from {bName}".format(ly=self.km.str_ly_range(self.baseSystem), j=self.system.str_gates(self.baseSystem, self.feed.service), bName=self.baseSystem.str_system_name()))

    def set_frame_color(self):
        s = (datetime.datetime.utcnow() - self.km.get_time()).total_seconds()
        if 0 <= s <= 60:
            self.color = discord.Color(12124259)
        elif 60 <= s <= 300:
            self.color = discord.Color(8454210)
        else:
            self.color = discord.Color(4128800)
        super().set_frame_color()

    def helper_routes(self, no_codeblock=False):
        if no_codeblock:
            row_template = "[{0}{1}]" + "({2})\n"
        else:
            row_template = "[```{0:<23}{1}```]" + "({2})"
        return_str = ""
        return_str += row_template.format("Titans/Supers", "", self.baseSystem.str_jmp_titan(self.system))
        return_str += row_template.format("Carriers/Dreads/FAX", "", self.baseSystem.str_jmp_carrier(self.system))
        return_str += row_template.format("Blops", "", self.baseSystem.str_jmp_blops(self.system))
        return_str += row_template.format("Gates ", self.system.str_gates(self.baseSystem, self.feed.service, True),
                                          self.baseSystem.str_dotlan_gates(self.system))
        if not no_codeblock:
            return_str += "\n**[zKill KM]({})**".format(self.km.str_zk_link())
        return return_str

    def run_filter(self):
        if (datetime.datetime.utcnow() - self.max_delta()) >= self.km.killmail_time:
            return False
        self.baseSystem = self.km.filter_system_ly(self.filters.object_filter_systems, self.in_system_ly)
        if self.baseSystem is None:
            return False
        self.list_typeGroup = self.filters.object_filter_groups + self.filters.object_filter_types
        tracked_ships = self.km.filter_attackers(self.km.object_attackers, self.list_typeGroup,
                                                 self.in_attackers_ship_group)
        if len(tracked_ships) == 0:
            return False
        __list_aff = self.filters.object_filter_alliances + self.filters.object_filter_corporations + self.filters.object_filter_characters
        self.tracked_hostiles = self.km.filter_attackers(tracked_ships, __list_aff, self.in_attackers_affiliation)
        if len(self.tracked_hostiles) == 0:
            return False
        return True

    def max_delta(self):
        return datetime.timedelta(minutes=self.feed_options.max_km_age)

    @classmethod
    def feed_specific_row_type(cls):
        return tb_capRadar

    @classmethod
    def appearance_options(cls):
        yield VisualCapRadarUtilityMinimal
        yield VisualCapRadarUtility
        yield VisualCapRadarCompact
        yield VisualCapRadarAbbreviated
        yield VisualCapRadarLinkOnly
        yield cls

    @classmethod
    def get_desc(cls):
        return "Full (Legacy) - The first/original Insight appearance (not recommended for new feeds or mobile). " \
               "Detailed count breakdown of tracked ship types, highest valued attacker details, system/location " \
               "details, and generated Dotlan routes from base system. Size: Very large"


from .VisualCapRadarCompact import VisualCapRadarCompact
from .VisualCapRadarLinkOnly import VisualCapRadarLinkOnly
from .VisualCapRadarUtility import VisualCapRadarUtility
from .VisualCapRadarUtilityMinimal import VisualCapRadarUtilityMinimal
from .VisualCapRadarAbbreviated import VisualCapRadarAbbreviated
