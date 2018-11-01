from .capRadar import *


class ProximityWatch(capRadar):

    def linked_visual_base(self):
        return VisualProximityWatch

    def get_linked_options(self):
        return Linked_Options.opt_pwatch(self)

    @classmethod
    def get_template_id(cls):
        return 10

    @classmethod
    def get_template_desc(cls):
        return "Proximity Watch - Tracks any hostile fleet activity near your base systems or in a selection of " \
               "systems, constellations, or regions. Proximity watches are ideal for finding potential fleets to " \
               "fight, tracking hostile fleet movement within your region, or alerting you of nearby hostiles" \
               " within a few jumps of your base systems."

    def __str__(self):
        return "Proximity Watch"

    @classmethod
    def feed_category(cls):
        return 1
