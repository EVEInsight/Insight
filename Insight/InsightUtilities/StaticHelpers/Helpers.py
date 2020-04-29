class Helpers(object):
    @staticmethod
    def get_nested_value(d: dict, default_value=None, *args):
        for k in args:
            try:
                d = d.get(k)
            except AttributeError:
                return default_value
        return d if d is not None else default_value