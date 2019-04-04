class StaticUtil(object):
    """static utility functions"""
    @staticmethod
    def filter_type(item_list: list, filter_type: type):
        """returns a list of items of filter_type from an existing item_list"""
        return [i for i in item_list if isinstance(i, filter_type)]
