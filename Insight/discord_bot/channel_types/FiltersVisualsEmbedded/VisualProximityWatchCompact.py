from .VisualProximityWatch import *


class VisualProximityWatchCompact(VisualProximityWatch):
    def make_header(self):
        h_count = len(self.tracked_hostiles)
        autHead = "{} hostile{} in {}".format(str(h_count), "s" if h_count > 1 else "", str(self.system))
        self.embed.set_author(name=autHead, url=self.km.str_zk_link(), icon_url=self.hv.str_highest_image(64))
        desc = '**[{hName}]({haZK})({haAfN})** in a **{hShip}** near **[{loc}]({locL})**.' \
            .format(hName=self.hv.str_pilot_name(), haZK=self.hv.str_pilot_zk(), haAfN=self.hv.str_highest_name(),
                    hShip=self.hv.str_ship_name(), loc=self.km.str_location_name(True), locL=self.system.str_dotlan_map())
        self.embed.description = desc
        self.embed.title = "{hShip} destroyed a {vS} in {sysR}".format(hShip=self.hv.str_ship_name(),
                                                                       vS=self.vi.str_ship_name(),sysR=str(self.system))
        self.embed.set_thumbnail(url=self.hv.str_ship_image(64))

    @classmethod
    def appearance_id(cls):
        return 3

    @classmethod
    def get_desc(cls):
        return "Compact - Null"
