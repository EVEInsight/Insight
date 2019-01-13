from .visual_capradar import *


class VisualCapRadarLinkOnly(visual_capradar):
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
        return 4

    @classmethod
    def get_desc(cls):
        return "Link-only - A direct killmail text link with no rich embed content. Size: Smallest"
