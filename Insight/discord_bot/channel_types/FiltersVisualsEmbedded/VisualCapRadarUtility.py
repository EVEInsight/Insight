from .visual_capradar import *


class VisualCapRadarUtility(visual_capradar):
    def make_text_heading(self):
        self.message_txt = "{}".format(self.mention_method())

    def field_overview(self):
        s_field = "```{}```".format(self.km.str_overview(self.tracked_hostiles, other=True, balance=True))
        af_field = "```{}```".format(
            self.km.str_overview(self.tracked_hostiles, affiliation=True, other=False, balance=True))
        self.embed.add_field(name="Ships - {}".format(self.km.str_total_involved()), value=s_field, inline=False)
        self.embed.add_field(name="Affiliation", value=af_field, inline=False)

    def field_victim(self):
        v_field = "Ship: [{S}]({Sl})\nPilot: [{P}]({Pl})\nCorp: [{C}]({Cl})\nAlliance: [{A}]({Al})".format(
            S=self.vi.str_ship_name(), Sl=self.vi.str_ship_zk(), P=self.vi.str_pilot_name(), Pl=self.vi.str_pilot_zk(),
            C=self.vi.str_corp_name(), Cl=self.vi.str_corp_zk(),
            A=self.vi.str_alliance_name(), Al=self.vi.str_alliance_zk())
        self.embed.add_field(name="Victim", value=v_field, inline=True)

    def field_attacker(self):
        a_field = "Ship: [{S}]({Sl})\nPilot: [{P}]({Pl})\nCorp: [{C}]({Cl})\nAlliance: [{A}]({Al})".format(
            S=self.hv.str_ship_name(), Sl=self.hv.str_ship_zk(), P=self.hv.str_pilot_name(), Pl=self.hv.str_pilot_zk(),
            C=self.hv.str_corp_name(), Cl=self.hv.str_corp_zk(),
            A=self.hv.str_alliance_name(), Al=self.hv.str_alliance_zk())
        self.embed.add_field(name="Attacker", value=a_field, inline=True)

    def field_details(self):
        d_field = "System: [{sN}]({sL})({rgN})\nCelestial: [{locN}]({loc_l})\nTime: {mAgo}\nKill: **[{shipN}]({kL})**".\
            format(sN=self.system.str_system_name(), sL=self.system.str_dotlan_map(), rgN=self.system.str_region_name(),
                   locN=self.km.str_location_name(True), loc_l=self.km.str_location_zk(),
                   mAgo=self.km.str_minutes_ago(True), shipN=self.vi.str_ship_name(), kL=self.km.str_zk_link())
        self.embed.add_field(name="Details", value=d_field, inline=True)

    def field_routes(self):
        self.embed.add_field(name="Routes", value=self.helper_routes(no_codeblock=True), inline=True)

    def make_header(self):
        authorH = "{haS} activity in {sysReg}".format(haS=self.hv.str_ship_name(), sysReg=str(self.system))
        self.embed.set_author(name=authorH, url=self.km.str_zk_link(), icon_url=self.hv.str_highest_image(64))
        self.field_overview()
        self.field_victim()
        self.field_attacker()
        self.field_details()
        self.field_routes()
        self.embed.description = " "
        self.embed.title = " "
        self.embed.set_thumbnail(url=self.hv.str_ship_image(64))

    def make_body(self):
        pass

    @classmethod
    def appearance_id(cls):
        return 2

    @classmethod
    def get_desc(cls):
        return "Utility - Fields: Attacking ship overview, affiliation overview, victim, highest valued attacker, " \
               "details(system, celestial, time), and Dotlan routes. Size: Large"
