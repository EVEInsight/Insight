from .visual_capradar import *


class VisualCapRadarFunctional(visual_capradar):
    def make_vars(self):
        super().make_vars()
        self.haShipName = self.km.fb_ship(self.highestAT)
        self.haPname = self.km.fb_Name(self.highestAT)
        self.haCname = self.km.fb_Corp(self.highestAT)
        self.haAname = self.km.fb_Alliance(self.highestAT)
        self.vShipName = self.km.fb_ship(self.km.object_victim)
        self.vPname = self.km.fb_Name(self.km.object_victim)
        self.vCname = self.km.fb_Corp(self.km.object_victim)
        self.vAname = self.km.fb_Alliance(self.km.object_victim)
        self.author_header = "{hS} activity in {kmSys}({kmRg})".format(hS=self.haShipName, kmSys=self.system_name,
                                                                       kmRg=self.region_name)
        self.location_name = self.km.str_location_name(name_only=True)
        self.attacking_ships = self.km.str_overview(self.tracked_hostiles, other=True)

    def make_links(self):
        super().make_links()
        self.vShipLink = "https://zkillboard.com/ship/{}/".format(self.km.fb_shipID(self.km.object_victim))
        self.haShipLink = "https://zkillboard.com/ship/{}/".format(self.km.fb_shipID(self.highestAT))
        self.vPlink = "https://zkillboard.com/character/{}/".format(self.km.fb_pID(self.km.object_victim))
        self.vClink = "https://zkillboard.com/corporation/{}/".format(self.km.fb_cID(self.km.object_victim))
        self.vAlink = "https://zkillboard.com/alliance/{}/".format(self.km.fb_aID(self.km.object_victim))
        self.haPlink = "https://zkillboard.com/character/{}/".format(self.km.fb_pID(self.highestAT))
        self.haClink = "https://zkillboard.com/corporation/{}/".format(self.km.fb_cID(self.highestAT))
        self.haAlink = "https://zkillboard.com/alliance/{}/".format(self.km.fb_aID(self.highestAT))
        self.locLink = "https://zkillboard.com/location/{}/".format(self.km.str_location_id())
        _dotlan_link = "http://evemaps.dotlan.net/jump/{ship},555/{base}:{target}".format(ship="{1}",
                                                                                          base=self.base_name,
                                                                                          target=self.system_name)
        _dotlan_gates = "http://evemaps.dotlan.net/route/{base}:{target}".format(base=self.base_name,
                                                                                 target=self.system_name)
        _row = "[{0}]" + "({})\n".format(_dotlan_link)
        self.dotlan_route_links = ""
        self.dotlan_route_links += _row.format("Titans/Supers", "Avatar")
        self.dotlan_route_links += _row.format("Carriers/Dreads/FAX", "Archon")
        self.dotlan_route_links += _row.format("Blops", "Redeemer")
        self.dotlan_route_links += "[Gates]({})".format(_dotlan_gates)

    def make_text_heading(self):
        self.message_txt = "{}".format(self.mention_method())

    def make_images(self):
        super().make_images()
        self.ship_image = "https://imageserver.eveonline.com/Render/{}_64.png".format(self.km.fb_shipID(self.highestAT))

    def make_header(self):
        self.embed.set_author(name=self.author_header, url=self.zk_kill, icon_url=self.thumbnail)
        self.embed.add_field(name="Overview", value="```{}```".format(self.attacking_ships), inline=False)
        v_field = "Ship: [{S}]({Sl})\nPilot: [{P}]({Pl})\nCorp: [{C}]({Cl})\nAlliance: [{A}]({Al})".format(
            S=self.vShipName, Sl=self.vShipLink, P=self.vPname, Pl=self.vPlink, C=self.vCname, Cl=self.vClink,
            A=self.vAname, Al=self.vAlink)
        self.embed.add_field(name="Victim", value=v_field, inline=True)
        a_field = "Ship: [{S}]({Sl})\nPilot: [{P}]({Pl})\nCorp: [{C}]({Cl})\nAlliance: [{A}]({Al})".format(
            S=self.haShipName, Sl=self.haShipLink, P=self.haPname, Pl=self.haPlink, C=self.haCname, Cl=self.haClink,
            A=self.haAname, Al=self.haAlink)
        self.embed.add_field(name="Attacker", value=a_field, inline=True)
        d_field = "System: [{SysName}]({SysLink})({RgName})\nCelestial: [{cName}]({cLink})\nTime: {mAgo}\nKill: **[KM]({kLi})**".format(
            SysName=self.system_name,
            SysLink=self.system_link, RgName=self.region_name, cName=self.location_name, cLink=self.locLink,
            mAgo=self.text_minutes_ago, kLi=self.zk_kill)
        self.embed.add_field(name="Details", value=d_field, inline=True)
        self.embed.add_field(name="Routes", value=self.dotlan_route_links, inline=True)
        self.embed.description = " "
        self.embed.title = " "
        self.embed.url = self.zk_kill
        self.embed.set_thumbnail(url=self.ship_image)
        self.embed.timestamp = self.km.killmail_time

    def make_body(self):
        self.embed.set_footer(text="{ly_aw} LYs from {bName}".format(ly_aw=self.ly_range, bName=self.base_name))

    @classmethod
    def appearance_id(cls):
        return 2

    @classmethod
    def get_desc(cls):
        return "Functional <-recommended - Less verbosity with all information and available routes. Size: Medium"
