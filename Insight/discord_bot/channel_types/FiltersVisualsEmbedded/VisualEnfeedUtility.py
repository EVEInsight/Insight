from .visual_enfeed import *


class VisualEnfeedUtility(visual_enfeed):
    def field_victim(self):
        v_field = ""
        v_field += "Ship: [{}]({})\n".format(self.vi.str_ship_name(), self.vi.str_ship_zk())\
            if self.vi.str_ship_name() else ""
        v_field += "Pilot: [{}]({})\n".format(self.vi.str_pilot_name(), self.vi.str_pilot_zk()) \
            if self.vi.str_pilot_name() else ""
        v_field += "Corp: [{}]({})\n".format(self.vi.str_corp_name(), self.vi.str_corp_zk())\
            if self.vi.str_corp_name() else ""
        v_field += "Alliance: [{}]({})".format(self.vi.str_alliance_name(), self.vi.str_alliance_zk())\
            if self.vi.str_alliance_name() else ""
        self.embed.add_field(name="Victim", value=v_field, inline=True)

    def field_fb(self):
        fb_field = ""
        fb_field += "Ship: [{}]({})\n".format(self.fb.str_ship_name(), self.fb.str_ship_zk())\
            if self.fb.str_ship_name() else ""
        fb_field += "Pilot: [{}]({})\n".format(self.fb.str_pilot_name(), self.fb.str_pilot_zk()) \
            if self.fb.str_pilot_name() else ""
        fb_field += "Corp: [{}]({})\n".format(self.fb.str_corp_name(), self.fb.str_corp_zk())\
            if self.fb.str_corp_name() else ""
        fb_field += "Alliance: [{}]({})".format(self.fb.str_alliance_name(), self.fb.str_alliance_zk())\
            if self.fb.str_alliance_name() else ""
        self.embed.add_field(name="Final Blow", value=fb_field, inline=True)

    def field_details(self):
        d_field = "System: [{sN}]({sL})({rgN})\nCelestial: [{locN}]({loc_l})\nInvolved: {invC}\nKM: **[{shipN}]({kL})**".\
            format(sN=self.system.str_system_name(), sL=self.system.str_dotlan_map(), rgN=self.system.str_region_name(),
                   locN=self.km.str_location_name(True), loc_l=self.km.str_location_zk(),
                   invC=self.km.str_total_involved(), shipN=self.vi.str_ship_name(), kL=self.km.str_zk_link())
        self.embed.add_field(name="Details", value=d_field, inline=True)

    def make_header(self):
        author_text = "Kill" if self.is_kill else "Loss"
        author_text += ": {vS} destroyed in {sysReg}".format(vS=self.vi.str_ship_name(), sysReg=str(self.system))
        self.embed.set_author(name=author_text, url=self.km.str_zk_link(), icon_url=self.vi.str_highest_image(64))
        self.field_victim()
        self.field_fb()
        self.field_details()
        self.embed.description = ""
        self.embed.title = ""
        self.embed.set_thumbnail(url=self.vi.str_ship_image(64))
        self.embed.set_footer(text="Value: {}".format(self.km.str_isklost()))

    def make_body(self):
        pass

    @classmethod
    def appearance_id(cls):
        return 5

    @classmethod
    def get_desc(cls):
        return "Utility - Basic killmail information with victim, final blow, and detail fields. Size: Medium"
