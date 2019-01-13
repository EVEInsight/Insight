from .VisualProximityWatch import *


class VisualProximityWatchAbbreviated(VisualProximityWatch):
    def make_header(self):
        invCount = "{tC}/{tI}".format(tC=str(len(self.tracked_hostiles)), tI=self.km.str_total_involved())
        e_desc = '**{haS} - [{haP}]({haP_l})({haAfi}) ({invC}) ->  {vS} -- [{sY}]({sL}) - [{locN}]({loc_l})  -- ' \
                 '[KM]({kmL})**'.format(vS=self.vi.str_ship_name(), haS=self.hv.str_ship_name(),
                                        haP=self.hv.str_pilot_name(), haP_l=self.hv.str_pilot_zk(),
                                        haAfi=self.hv.str_highest_name(), invC=invCount,
                                        sY=str(self.system), sL=self.system.str_dotlan_map(),
                                        locN=self.km.str_location_name(True), loc_l=self.km.str_location_zk(),
                                        kmL=self.km.str_zk_link())
        self.embed.description = e_desc
        self.embed.title = ""
        self.embed.set_thumbnail(url=self.hv.str_ship_image(32))

    @classmethod
    def appearance_id(cls):
        return 60

    @classmethod
    def get_desc(cls):
        return "Abbreviated - null Size: Small"  # todo
