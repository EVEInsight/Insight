from .Visual_ProximityIntel import *
from .VisualEnfeedCompact import VisualEnfeedCompact


class Visual_ProximityIntel_Compact(VisualEnfeedCompact, Visual_ProximityIntel):
    def internal_list_options(self):
        Visual_ProximityIntel.internal_list_options(self)

    def run_filter(self):
        return Visual_ProximityIntel.run_filter(self)

    def set_frame_color(self):
        self.set_kill()
        VisualEnfeedCompact.set_frame_color(self)

    @classmethod
    def feed_specific_row_type(cls):
        return Visual_ProximityIntel.feed_specific_row_type()

    @classmethod
    def appearance_id(cls):
        return 1

    @classmethod
    def get_desc(cls):
        return "Entity Feed Compact - Display as if in entity feed instead of tracking information."
