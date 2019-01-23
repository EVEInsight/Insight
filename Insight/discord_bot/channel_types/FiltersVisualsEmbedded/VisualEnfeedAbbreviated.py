from .visual_enfeed import *


class VisualEnfeedAbbreviated(visual_enfeed):
    def make_header(self):
        e_desc = '**{vS} - [{vP}]({vP_l})({vAfi}) <- {fbS} - [{fbP}]({fbP_l})' \
                 '({fbAfi}) ({invC}) -- [{sY}]({sL}) -- [KM]({kmL})**'.format(vS=self.vi.str_ship_name(), vP=self.vi.str_pilot_name(), vP_l=self.vi.str_pilot_zk(), vAfi=self.vi.str_highest_name(), fbS=self.fb.str_ship_name(),
                    fbP=self.fb.str_pilot_name(), fbP_l=self.fb.str_pilot_zk(),
                    fbAfi=self.fb.str_highest_name(), invC=self.km.str_total_involved(), sY=str(self.system), sL=self.system.str_dotlan_map(), kmL=self.km.str_zk_link())
        self.embed.description = e_desc
        self.embed.title = ""
        self.embed.set_thumbnail(url=self.vi.str_ship_image(32))
        self.embed.set_footer(text="Value: {}".format(self.km.str_isklost()))

    def make_body(self):
        pass

    @classmethod
    def appearance_id(cls):
        return 60

    @classmethod
    def get_desc(cls):
        return "Abbreviated - Minimal verbosity with victim/attacker names & affiliation. " \
               "Includes KM, affiliation, & Dotlan map links. Size: Small"
