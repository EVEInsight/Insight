from .capRadar import *


class ProximityWatch(capRadar):
    @classmethod
    def get_template_id(cls):
        return 10

    @classmethod
    def get_template_desc(cls):
        return "Proximity Watch - Null"

    def __str__(self):
        return "Proximity Watch"

