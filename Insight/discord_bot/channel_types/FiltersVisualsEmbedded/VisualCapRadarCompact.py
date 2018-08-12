from .visual_capradar import *


class VisualCapRadarCompact(visual_capradar):
    def make_images(self):
        super().make_images()
        self.ship_image = "https://imageserver.eveonline.com/Render/{}_64.png".format(str(self._highestAT.ship_type_id))

    def make_header(self):
        autHead = "{hS} activity in {kmSys}({kmRg}). {tC}/{tI} tracked ships.". \
            format(hS=self.haShip, kmSys=self.system_name, kmRg=self.region_name, tC=str(len(self.tracked_hostiles)),
                   tI=str(self.total_involved))
        self.embed.set_author(name=autHead, url=self.zk_kill, icon_url=self.thumbnail)
        __desc = '**[{hName}]({haZK})({hCorp})**{hAl} in a **{hShip}** [{lName}]({system_link})' \
            .format(system_link=self.system_link, lName=self.location_name, hName=self.haName,
                    haZK=self.haZK, hCorp=self.haCorp, hAl=self.haAli, hShip=self.haShip)
        self.embed.description = __desc
        self.embed.title = " "
        self.embed.url = self.zk_kill
        self.embed.set_thumbnail(url=self.ship_image)
        self.embed.timestamp = self.km.killmail_time

    def make_body(self):
        pass

    @classmethod
    def appearance_id(cls):
        return 3

    @classmethod
    def get_desc(cls):
        return "Compact - Attacker affiliation, shiptype, nearest celestial, color time indicator, and zKillboard link. Size: Small"
