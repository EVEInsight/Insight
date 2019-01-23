from .visual_capradar import *


class VisualCapRadarAbbreviated(visual_capradar):
    def make_text_heading(self):
        self.message_txt = "{}".format(self.mention_method())

    def make_header(self):
        e_desc = '**{haS} - [{haP}]({haP_l})({haAfi}) ->  {vS} -- [{sY}]({sL}) - [{locN}]({loc_l})  -- ' \
                 '[KM]({kmL})**'.format(vS=self.vi.str_ship_name(), haS=self.hv.str_ship_name(),
                                        haP=self.hv.str_pilot_name(), haP_l=self.hv.str_pilot_zk(),
                                        haAfi=self.hv.str_highest_name(), sY=str(self.system),
                                        sL=self.baseSystem.str_jmp_titan(self.system),
                                        locN=self.km.str_location_name(True), loc_l=self.km.str_location_zk(),
                                        kmL=self.km.str_zk_link())
        self.embed.description = e_desc
        self.embed.title = ""
        self.embed.set_thumbnail(url=self.hv.str_ship_image(32))

    def make_body(self):
        pass

    def make_footer(self):
        dist_txt = "{ly} LY/{j} J -> {bName}".format(ly=self.km.str_ly_range(self.baseSystem), j=self.system.str_gates(self.baseSystem, self.feed.service), bName=self.baseSystem.str_system_name())
        inv_txt = "Inv: {tC}/{tI}".format(tC=str(len(self.tracked_hostiles)), tI=self.km.str_total_involved())
        self.embed.set_footer(text="{} | {}".format(dist_txt, inv_txt))

    @classmethod
    def appearance_id(cls):
        return 60

    @classmethod
    def get_desc(cls):
        return "Abbreviated - Minimal verbosity with attacker name, ship, & affiliation. Includes KM, affiliation, " \
               "location, & Dotlan super route links. Size: Small"
