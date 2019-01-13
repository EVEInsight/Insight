from .VisualProximityWatch import *


class VisualProximityWatchAbbreviated(VisualProximityWatch):
    def make_header(self):
        e_desc = '**{haS} - [{haP}]({haP_l})({haAfi}) ->  {vS} -- [{sY}]({sL}) - [{locN}]({loc_l})  -- ' \
                 '[KM]({kmL})**'.format(vS=self.vi.str_ship_name(), haS=self.hv.str_ship_name(),
                                        haP=self.hv.str_pilot_name(), haP_l=self.hv.str_pilot_zk(),
                                        haAfi=self.hv.str_highest_name(), sY=str(self.system),
                                        sL=self.system.str_dotlan_map(), locN=self.km.str_location_name(True),
                                        loc_l=self.km.str_location_zk(), kmL=self.km.str_zk_link())
        self.embed.description = e_desc
        self.embed.title = ""
        self.embed.set_thumbnail(url=self.hv.str_ship_image(32))

    def make_footer(self):
        footer_str = str(self.base_sysConstReg)
        if isinstance(self.base_sysConstReg, tb_systems):
            dist = self.system.gate_range(self.base_sysConstReg, self.feed.service)
            if dist is not None:
                if dist > 0:
                    footer_str = "{} jump{} -> {}".format(str(dist), "" if dist == 1 else "s", self.base_sysConstReg.str_system_name())
                else:
                    footer_str = "In {}".format(str(self.base_sysConstReg))
        inv_txt = "Inv: {tC}/{tI}".format(tC=str(len(self.tracked_hostiles)), tI=self.km.str_total_involved())
        self.embed.set_footer(text="{} | {}".format(footer_str, inv_txt))

    @classmethod
    def appearance_id(cls):
        return 60

    @classmethod
    def get_desc(cls):
        return "Abbreviated - null Size: Small"  # todo
