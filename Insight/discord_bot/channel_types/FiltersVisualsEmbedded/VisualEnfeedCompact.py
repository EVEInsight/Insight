from .visual_enfeed import *


class VisualEnfeedCompact(visual_enfeed):
    def make_header(self):
        author_text = "Kill" if self.is_kill else "Loss"
        self.embed.set_author(name=author_text, url=self.km.str_zk_link(), icon_url=self.vi.str_highest_image(64))
        e_desc = '**[{vP}]({vP_l})({vAfi})** lost their **{vS}** to **[{fbP}]({fbP_l})' \
                 '({fbAfi})** flying in a **{fbS}** {inv_str}.' \
            .format(vP=self.vi.str_pilot_name(), vP_l=self.vi.str_pilot_zk(), vAfi=self.vi.str_highest_name(),
                    vS=self.vi.str_ship_name(), fbP=self.fb.str_pilot_name(), fbP_l=self.fb.str_pilot_zk(),
                    fbAfi=self.fb.str_highest_name(), fbS=self.fb.str_ship_name(), inv_str=self.km.str_attacker_count())
        self.embed.description = e_desc
        self.embed.title = "{vS} destroyed in {sysReg}".format(vS=self.vi.str_ship_name(), sysReg=str(self.system))
        self.embed.url = self.km.str_zk_link()
        self.embed.set_thumbnail(url=self.vi.str_ship_image(64))
        self.embed.timestamp = self.km.get_time()
        self.embed.set_footer(text="Value: {}".format(self.km.str_isklost()))

    def make_body(self):
        pass

    @classmethod
    def appearance_id(cls):
        return 3

    @classmethod
    def get_desc(cls):
        return "Compact <-recommended - Basic killmail information with value, color sidebar, and zKillboard link. Size: Small"
