from .VisualEnfeedCompact import *


class VisualEnfeedCompactTracked(VisualEnfeedCompact):
    def make_header(self):
        if len(self.tracked_attackers) > 0:
            a: tb_attackers = self.tracked_attackers[0]
            trackCount = "({}/{})".format(len(self.tracked_attackers), self.km.str_total_involved())
            author_text = "Kill" if self.is_kill else "Loss"
            self.embed.set_author(name=author_text, url=self.km.str_zk_link(), icon_url=self.vi.str_highest_image(64))
            e_desc = '**[{vP}]({vP_l})({vAfi})** lost their **{vS}** to **[{fbP}]({fbP_l})' \
                     '({fbAfi})** in a **{fbS}**. **{inv_str}**' \
                .format(vP=self.vi.str_pilot_name(), vP_l=self.vi.str_pilot_zk(), vAfi=self.vi.str_highest_name(),
                        vS=self.vi.str_ship_name(), fbP=a.str_pilot_name(), fbP_l=a.str_pilot_zk(),
                        fbAfi=a.str_highest_name(), fbS=a.str_ship_name(), inv_str=trackCount)
            self.embed.description = e_desc
            self.embed.title = "{vS} destroyed in {sysReg}".format(vS=self.vi.str_ship_name(), sysReg=str(self.system))
            self.embed.set_thumbnail(url=self.vi.str_ship_image(64))
            self.embed.set_footer(text="Value: {}".format(self.km.str_isklost()))
        else:
            super().make_header()

    @classmethod
    def appearance_id(cls):
        return 7

    @classmethod
    def get_desc(cls):
        return "Compact Tracked - Compact appearance that displays the tracked entity who participated in the " \
               "mail instead of the final blow."
