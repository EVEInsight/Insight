from .VisualProximityWatch import *


class VisualProximityWatchMinimal(VisualProximityWatch):
    def make_header(self):
        author_header = "{hS} activity in {SysR}".format(hS=self.hv.str_ship_name(), SysR=str(self.system))
        self.embed.set_author(name=author_header, url=self.km.str_zk_link(), icon_url=self.hv.str_highest_image(64))
        self.field_overview()
        self.field_details()
        self.embed.description = " "
        self.embed.title = " "
        self.embed.set_thumbnail(url=self.hv.str_ship_image(64))

    @classmethod
    def appearance_id(cls):
        return 4

    @classmethod
    def get_desc(cls):
        return "Utility minimal <-recommended - A minimal version of the utility appearance with the victim and" \
               " highest valued attacker fields removed. Size: Medium"
