from .VisualProximityWatch import *
from .VisualEnfeedCompact import VisualEnfeedCompact


class VisualProximityWatchEFCompact(VisualEnfeedCompact, VisualProximityWatch):
    def internal_list_options(self):
        VisualProximityWatch.internal_list_options(self)

    def run_filter(self):
        self.set_kill()
        return VisualProximityWatch.run_filter(self)

    @classmethod
    def feed_specific_row_type(cls):
        return VisualProximityWatch.feed_specific_row_type()

    def set_frame_color(self):
        super(VisualProximityWatch, self).set_frame_color()  # call base method

    @classmethod
    def appearance_id(cls):
        return 1

    @classmethod
    def get_desc(cls):
        return "Entity-like compact - Uses entity feed compact appearance to display killmail instead of " \
               "tracking info. Size: Small "
