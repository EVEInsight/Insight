from .VisualEnfeedCompact3 import *


class VisualEnfeedCompactTracked(VisualEnfeedCompact3):
    def make_header(self):
        super().make_header()
        if len(self.tracked_attackers) > 0:
            a: tb_attackers = self.tracked_attackers[0]
            f = '\n\n**[{P}]({P_l})({Afi})** in a **{S}** {inv_str}.'.format(P=a.str_pilot_name(),
                                                                                   P_l=a.str_pilot_zk(),
                                                                                   Afi=a.str_highest_name(),
                                                                                   S=a.str_ship_name(),
                                                                                   inv_str=self.km.str_attacker_count(self.tracked_attackers))
            self.embed.description += f

    @classmethod
    def appearance_id(cls):
        return 7

    @classmethod
    def get_desc(cls):
        return "Compact Tracked - Compact 3 appearance with tracked entity participant information."
