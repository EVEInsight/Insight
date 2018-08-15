from .visual_enfeed import *


class VisualEnfeedCompact(visual_enfeed):
    def make_header(self):
        self.embed.set_author(name=self.author_text, url=self.zk_kill, icon_url=self.im_victim_corpAli)
        __desc = '**[{pilot_name}]({victimP_zk})({corp_name})** lost their **{ship_name}** to **[{fb_name}]({fbP_zk})' \
                 '({fb_corp})** flying in a **{fb_ship}** {inv_str}.' \
            .format(ship_name=self.ship_name, pilot_name=self.pilot_name, victimP_zk=self.victimP_zk,
                    corp_name=self.corp_name, fb_name=self.fb_name, fbP_zk=self.fbP_zk, fb_corp=self.fb_Corp,
                    fb_ship=self.fb_ship, inv_str=self.inv_str)
        self.embed.description = __desc
        self.embed.title = "**{ship_name} destroyed in {system_name}({region_name})**".format(ship_name=self.ship_name,
                                                                                              system_name=self.system_name,
                                                                                              region_name=self.region_name)
        self.embed.url = self.zk_kill
        self.embed.set_thumbnail(
            url="https://imageserver.eveonline.com/Render/{}_64.png".format(str(self.km.object_victim.ship_type_id)))
        self.embed.timestamp = self.km.killmail_time
        self.embed.set_footer(text="Value: {}".format(self.isk_lost))

    def make_body(self):
        pass

    @classmethod
    def appearance_id(cls):
        return 3

    @classmethod
    def get_desc(cls):
        return "Compact - Basic killmail information with value, color sidebar, and zKillboard link. Size: Small"
