from .VisualCapRadarUtility import *


class VisualCapRadarUtilityMinimal(VisualCapRadarUtility):
    def make_header(self):
        authorH = "{haS} activity in {sysReg}".format(haS=self.hv.str_ship_name(), sysReg=str(self.system))
        self.embed.set_author(name=authorH, url=self.km.str_zk_link(), icon_url=self.hv.str_highest_image(64))
        self.field_overview()
        self.field_details()
        self.field_routes()
        self.embed.description = " "
        self.embed.title = " "
        self.embed.set_thumbnail(url=self.hv.str_ship_image(64))

    @classmethod
    def appearance_id(cls):
        return 5

    @classmethod
    def get_desc(cls):
        return "Utility minimal <-recommended - A minimal version of the utility appearance with the victim and " \
               "highest valued attacker fields removed. Size: Medium"
