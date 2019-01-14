import os


class ResourceRoot(object):
    @classmethod
    def get_path(cls):
        return os.path.dirname(os.path.abspath(__file__))
