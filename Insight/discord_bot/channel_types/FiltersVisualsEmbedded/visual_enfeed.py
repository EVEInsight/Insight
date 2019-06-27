from .FiltersVisualsEmbedded import *


class visual_enfeed(base_visual):

    def __init__(self, km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object):
        super().__init__(km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object)
        self.is_kill = False
        self.tracked_attackers = []

    def internal_list_options(self):
        super().internal_list_options()
        self.in_attackers_affiliation = internal_options.use_whitelist.value

    def set_loss(self):
        self.is_kill = False
        self.color = discord.Color(16711680)

    def set_kill(self):
        self.is_kill = True
        self.color = discord.Color(65299)

    def make_text_heading(self):
        self.message_txt = "{}".format(self.mention_method())

    def make_header(self):
        author_text = "Kill" if self.is_kill else "Loss"
        self.embed.set_author(name=author_text, url=self.km.str_zk_link(), icon_url=self.vi.str_highest_image(64))
        body_desc = '**{vS}** destroyed in **[{sysN}]({systL})**({rgN})\n\n**[{vP}]({vP_l})' \
            '({vAfi})** lost their **{vS}** to **[{fbP}]({fbP_l})({fbAfi})** flying in a **{fbS}** {inv_str}.\n\n' \
            .format(vS=self.vi.str_ship_name(), sysN=self.system.str_system_name(), systL=self.system.str_dotlan_map(),
                    rgN=self.system.str_region_name(), vP=self.vi.str_pilot_name(), vP_l=self.vi.str_pilot_zk(),
                    vAfi=self.vi.str_highest_name(), fbP=self.fb.str_pilot_name(), fbP_l=self.fb.str_pilot_zk(),
                    fbAfi=self.fb.str_highest_name(), fbS=self.fb.str_ship_name(), inv_str=self.km.str_attacker_count())
        self.embed.description = body_desc
        self.embed.title = " "
        self.embed.set_thumbnail(url=self.vi.str_pilot_image(64))
        self.embed.set_image(url=self.vi.str_ship_image(128))

    def make_body(self):
        field_body = "```{Ship:<14}{vS}\n" \
                       "{Name:<14}{vP}\n" \
                       "{Corp:<14}{vC}\n{Alliance:<14}{vA}\n{Damage_Taken:<14}{damage_taken}\n" \
                       "{Involved:<14}{inv}\n{ISK_Lost:<14}{isk_lost}\n{Time:<14}{min_ago}```**[zKill KM]({zk})**" \
            .format(Ship='Ship:', Name="Name:", Corp="Corp:", Alliance="Alliance:", Damage_Taken="Damage Taken:",
                    Involved="Involved:", ISK_Lost="ISK Lost:", Time="Time:", zk=self.km.str_zk_link(),
                    vS=self.vi.str_ship_name(), vP=self.vi.str_pilot_name(), vC=self.vi.str_corp_name(),
                    vA=self.vi.str_alliance_name(), damage_taken=self.km.str_damage(), inv=self.km.str_total_involved(),
                    isk_lost=self.km.str_isklost(), min_ago=self.km.str_minutes_ago())
        self.embed.add_field(name="**Details**", value=field_body, inline=False)

    def make_footer(self):
        pass

    def run_filter(self):
        if (datetime.datetime.utcnow() - self.max_delta()) >= self.km.killmail_time:
            return False
        if self.feed_options.minValue > self.km.totalValue:
            return False
        if self.feed_options.maxValue < self.km.totalValue:
            return False
        list_type_group = self.filters.object_filter_types + self.filters.object_filter_groups
        if not self.km.filter_loss(list_type_group, self.in_victim_ship_group):  # if false/contained in cat blacklist ignore posting
            return False
        __list_systems = self.filters.object_filter_systems + self.filters.object_filter_regions
        match_syst = self.km.filter_system(__list_systems, self.in_system_nonly)
        if match_syst is None:
            return False
        __list_aff = self.filters.object_filter_alliances + self.filters.object_filter_corporations + self.filters.object_filter_characters
        if self.km.filter_victim(self.km.object_victim,filter_list=__list_aff,using_blacklist=self.in_victim_affiliation) is None: #affiliated is victim/loss
            self.set_loss()
            if self.feed_options.show_mode == enum_kmType.kills_only:
                return False
            if self.feed_options.show_mode == enum_kmType.losses_only or self.feed_options.show_mode == enum_kmType.show_both:
                return True
        else: #km victim is not affiliated/kill
            self.set_kill()
            if self.feed_options.show_mode == enum_kmType.losses_only:
                return False
            self.tracked_attackers = self.km.filter_attackers(self.km.object_attackers,filter_list=__list_aff,using_blacklist=self.in_attackers_affiliation)
            if len(self.tracked_attackers) > 0:
                return True
            else:
                return False
        return False

    def max_delta(self):
        return datetime.timedelta(days=1)

    @classmethod
    def feed_specific_row_type(cls):
        return tb_enfeed

    @classmethod
    def get_desc(cls):
        return "Full (Legacy) - The first/original Insight appearance (not recommended for new feeds or mobile). " \
               "Detailed killmail overview, pilot and ship images, color sidebar, and zKillboard/Dotlan links with " \
               "large fields and images. Size: Very large"

    @classmethod
    def appearance_options(cls):
        yield VisualEnfeedCompact
        yield VisualEnfeedCompact2
        yield VisualEnfeedCompact3
        yield VisualEnfeedCompactTracked
        yield VisualEnfeedAbbreviated
        yield VisualEnfeedUtility
        yield VisualEnfeedLinkOnly
        yield cls


from .VisualEnfeedCompact import VisualEnfeedCompact
from .VisualEnfeedLinkOnly import VisualEnfeedLinkOnly
from .VisualEnfeedUtility import VisualEnfeedUtility
from .VisualEnfeedCompact2 import VisualEnfeedCompact2
from .VisualEnfeedCompact3 import VisualEnfeedCompact3
from .VisualEnfeedAbbreviated import VisualEnfeedAbbreviated
from .VisualEnfeedEnfeedCompactTracked import VisualEnfeedCompactTracked
