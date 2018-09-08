from .visual_capradar import *


class VisualCapRadarFunctional(visual_capradar):
    def make_text_heading(self):
        self.message_txt = "{}".format(self.mention_method())

    def make_header(self):
        authorH = "{haS} activity in {sysReg}".format(haS=self.hv.str_ship_name(), sysReg=str(self.system))
        self.embed.set_author(name=authorH, url=self.km.str_zk_link(), icon_url=self.hv.str_highest_image(64))
        ov_field = "```{}```".format(self.km.str_overview(self.tracked_hostiles, other=True))
        v_field = "Ship: [{S}]({Sl})\nPilot: [{P}]({Pl})\nCorp: [{C}]({Cl})\nAlliance: [{A}]({Al})".format(
            S=self.vi.str_ship_name(), Sl=self.vi.str_ship_zk(), P=self.vi.str_pilot_name(), Pl=self.vi.str_pilot_zk(),
            C=self.vi.str_corp_name(), Cl=self.vi.str_corp_zk(),
            A=self.vi.str_alliance_name(), Al=self.vi.str_alliance_zk())
        a_field = "Ship: [{S}]({Sl})\nPilot: [{P}]({Pl})\nCorp: [{C}]({Cl})\nAlliance: [{A}]({Al})".format(
            S=self.hv.str_ship_name(), Sl=self.hv.str_ship_zk(), P=self.hv.str_pilot_name(), Pl=self.hv.str_pilot_zk(),
            C=self.hv.str_corp_name(), Cl=self.hv.str_corp_zk(),
            A=self.hv.str_alliance_name(), Al=self.hv.str_alliance_zk())
        d_field = "System: [{sN}]({sL})({rgN})\nCelestial: [{locN}]({loc_l})\nTime: {mAgo}\nKill: **[KM]({kL})**".\
            format(sN=self.system.str_system_name(), sL=self.system.str_dotlan_map(), rgN=self.system.str_region_name(),
                   locN=self.km.str_location_name(True), loc_l=self.km.str_location_zk(),
                   mAgo=self.km.str_minutes_ago(True), kL=self.km.str_zk_link())
        self.embed.add_field(name="Overview", value=ov_field, inline=False)
        self.embed.add_field(name="Victim", value=v_field, inline=True)
        self.embed.add_field(name="Attacker", value=a_field, inline=True)
        self.embed.add_field(name="Details", value=d_field, inline=True)
        self.embed.add_field(name="Routes", value=self.helper_routes(), inline=True)
        self.embed.description = " "
        self.embed.title = " "
        self.embed.set_thumbnail(url=self.hv.str_ship_image(64))

    def make_body(self):
        pass

    def helper_routes(self):
        row_template = "[{0}]" + "({1})\n"
        return_str = ""
        return_str += row_template.format("Titans/Supers", self.baseSystem.str_jmp_titan(self.system))
        return_str += row_template.format("Carriers/Dreads/FAX", self.baseSystem.str_jmp_carrier(self.system))
        return_str += row_template.format("Blops", self.baseSystem.str_jmp_blops(self.system))
        return_str += row_template.format("Gates", self.baseSystem.str_dotlan_gates(self.system))
        return return_str

    @classmethod
    def appearance_id(cls):
        return 2

    @classmethod
    def get_desc(cls):
        return "Functional <-recommended - Less verbosity with all information and available routes. Size: Medium"
