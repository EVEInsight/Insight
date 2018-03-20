import datetime


class limiter(object):
    def __init__(self, minutes_decay=5):
        """minutes_decay must be int"""
        assert isinstance(minutes_decay, int)
        self.decay = minutes_decay
        self.items = {}

    def __insert_item(self, item):
        self.items[item] = datetime.datetime.utcnow()

    def __get_item(self, item):
        return self.items.get(item)

    def item_decayed(self, item):
        val = self.__get_item(item)
        if val is None:
            self.__insert_item(item)
            return True
        else:
            if val > (datetime.datetime.utcnow() - datetime.timedelta(minutes=self.decay)):
                return False
            else:
                self.__insert_item(item)
                return True
