from .Visual_ProximityIntel import *


class Visual_ProximityIntel_LinkOnly(Visual_ProximityIntel):
    def make_text_heading(self):
        self.text_only = True
        self.message_txt = "{} {}".format(self.mention_method(), self.km.str_zk_link())

    def make_header(self):
        pass

    def make_body(self):
        pass

    def make_footer(self):
        pass

    @classmethod
    def appearance_id(cls):
        return 2

    @classmethod
    def get_desc(cls):
        return "Link-only - A direct killmail link with no rich embed content. Size: Smallest"
