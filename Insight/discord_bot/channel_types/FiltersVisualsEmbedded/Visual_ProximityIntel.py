from .FiltersVisualsEmbedded import *


class Visual_ProximityIntel(base_visual):
    def __init__(self, km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object):
        super().__init__(km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object)
        self.tracked_hostiles = []
        self.base_sysConstReg = None

    def internal_list_options(self):
        super().internal_list_options()
        self.in_attackers_affiliation = internal_options.use_blacklist.value
        self.in_system_nonly = internal_options.use_whitelist.value

    def make_vars(self):
        super().make_vars()
        self.fb: tb_attackers = self.km.get_final_blow()
        self.vi: tb_victims = self.km.get_victim()
        self.hv: tb_attackers = self.km.get_highest_attacker(self.tracked_hostiles)
        self.system: tb_systems = self.km.get_system()

    def make_text_heading(self):
        self.message_txt = "{}".format(self.mention_method())

    def make_header(self):
        author_header = "{hS} activity in {SysR}".format(hS=self.hv.str_ship_name(), SysR=str(self.system))
        self.embed.set_author(name=author_header, url=self.km.str_zk_link(), icon_url=self.hv.str_highest_image(64))
        self.embed.add_field(name="Ships", value="```{}```".format(self.km.str_overview(self.tracked_hostiles, other=True, balance=True)),
                             inline=False)
        self.embed.add_field(name="Affiliation", value="```{}```".format(self.km.str_overview(self.tracked_hostiles, True, True, True)),
                             inline=False)
        v_field = "Ship: [{S}]({Sl})\nPilot: [{P}]({Pl})\nCorp: [{C}]({Cl})\nAlliance: [{A}]({Al})".format(
            S=self.vi.str_ship_name(), Sl=self.vi.str_ship_zk(), P=self.vi.str_pilot_name(), Pl=self.vi.str_pilot_zk(), C=self.vi.str_corp_name(), Cl=self.vi.str_corp_zk(),
            A=self.vi.str_alliance_name(), Al=self.vi.str_alliance_zk())
        self.embed.add_field(name="Victim", value=v_field, inline=True)
        a_field = "Ship: [{S}]({Sl})\nPilot: [{P}]({Pl})\nCorp: [{C}]({Cl})\nAlliance: [{A}]({Al})".format(
            S=self.hv.str_ship_name(), Sl=self.hv.str_ship_zk(), P=self.hv.str_pilot_name(), Pl=self.hv.str_pilot_zk(), C=self.hv.str_corp_name(), Cl=self.hv.str_corp_zk(),
            A=self.hv.str_alliance_name(), Al=self.hv.str_alliance_zk())
        self.embed.add_field(name="Attacker", value=a_field, inline=True)
        d_field = "System: [{SysName}]({SysLink})({RgName})\nCelestial: [{cName}]({cLink})\nTime: {mAgo}\nKill: **[KM]({kLi})**".format(
            SysName=self.system.str_system_name(),
            SysLink=self.system.str_dotlan(), RgName=self.system.str_region_name(), cName=self.km.str_location_name(True), cLink=self.km.str_location_zk(),
            mAgo=self.km.str_minutes_ago(True), kLi=self.km.str_zk_link())
        self.embed.add_field(name="Details", value=d_field, inline=True)
        self.embed.description = " "
        self.embed.title = " "
        self.embed.url = self.km.str_zk_link()
        self.embed.set_thumbnail(url=self.hv.str_ship_image(64))
        self.embed.timestamp = self.km.killmail_time

    def make_body(self):
        if isinstance(self.base_sysConstReg, tb_systems):
            prefix = "In system:"
        elif isinstance(self.base_sysConstReg, tb_constellations):
            prefix = "In constellation:"
        else:
            prefix = "In region:"
        self.embed.set_footer(text="{} {}".format(prefix, str(self.base_sysConstReg)))

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
        yield Visual_ProximityIntel_Compact
        yield Visual_ProximityIntel_EFCompact
        yield Visual_ProximityIntel_LinkOnly

    @classmethod
    def get_desc(cls):
        return "Utility - Null"


from .Visual_ProximityIntel_Compact import Visual_ProximityIntel_Compact
from .Visual_ProximityIntel_EFCompact import Visual_ProximityIntel_EFCompact
from .Visual_ProximityIntel_LinkOnly import Visual_ProximityIntel_LinkOnly
