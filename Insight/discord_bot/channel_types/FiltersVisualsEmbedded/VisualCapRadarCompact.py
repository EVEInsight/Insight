from .visual_capradar import *


class VisualCapRadarCompact(visual_capradar):
    def make_vars(self):
        super().make_vars()
        self.super_route = "http://evemaps.dotlan.net/jump/Avatar,555/{base}:{target}".format(base=self.base_name,
                                                                                              target=self.system_name)
        if self.highestAT.alliance_id is not None:
            self.haAFFname = self.km.fb_Alliance(self.highestAT)
        else:
            self.haAFFname = self.haCorp
        loc_name = self.km.str_location_name(name_only=True)
        if loc_name:
            self.location_name = " near **[{}]({}).**".format(loc_name, self.super_route)
        else:
            self.location_name = " in **[{}]({}).**".format(self.system_name, self.super_route)

    def make_text_heading(self):
        self.message_txt = "{}".format(self.mention_method())

    def make_images(self):
        super().make_images()
        self.ship_image = "https://imageserver.eveonline.com/Render/{}_64.png".format(str(self.highestAT.ship_type_id))

    def make_header(self):
        autHead = "{tC} of {tI} in tracked ships". \
            format(tC=str(len(self.tracked_hostiles)), tI=str(self.total_involved))
        self.embed.set_author(name=autHead, url=self.zk_kill, icon_url=self.thumbnail)
        __desc = '**[{hName}]({haZK})({haAfN})** in a **{hShip}**{loc}' \
            .format(vS=self.ship_name, syName=self.system_name, rgName=self.region_name, zkL=self.zk_kill,
                    hName=self.haName, haZK=self.haZK, haAfN=self.haAFFname, hShip=self.haShip, loc=self.location_name)
        self.embed.description = __desc
        self.embed.title = "{hShip} destroyed a {vS} in {syName}({rgName})".format(vS=self.ship_name,
                                                                                   syName=self.system_name,
                                                                                   rgName=self.region_name,
                                                                                   hShip=self.haShip)
        self.embed.url = self.zk_kill
        self.embed.set_thumbnail(url=self.ship_image)
        self.embed.timestamp = self.km.killmail_time

    def make_body(self):
        self.embed.set_footer(text="{ly_aw} LYs from {bName}".format(ly_aw=self.ly_range, bName=self.base_name))

    @classmethod
    def appearance_id(cls):
        return 3

    @classmethod
    def get_desc(cls):
        return "Compact - Attacker ship/affiliation, nearest celestial, kill link, and super jump route. Size: Small"
