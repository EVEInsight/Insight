from .visual_enfeed import *


class VisualEnfeedLinkOnly(visual_enfeed):
    def make_text_heading(self):
        self.text_only = True
        self.message_txt = "{} {}".format(self.mention_method(), self.zk_kill)

    def make_header(self):
        pass

    def make_body(self):
        pass

    @classmethod
    def appearance_id(cls):
        return 4

    @classmethod
    def get_desc(cls):
        return "Link-only - A direct killmail link with no rich embed content. Size: Smallest"
