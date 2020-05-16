from operator import itemgetter
from collections import OrderedDict


class TrackingBucket(object):
    def __init__(self, key_id_name: str, key_data_name: str, value_as_list=False, unknown_overflow=True,
                 ordered_dict_sort_key=None):
        self.nested_key_id_name = key_id_name
        self.nested_key_data_name_1 = key_data_name
        self.unknown_overflow = unknown_overflow
        self.ordered_dict_sort_key = self.nested_key_id_name if not ordered_dict_sort_key else ordered_dict_sort_key
        self.list_value = value_as_list
        self.data = {}
        self.total = 0

    def add_item(self, key_name, add_value=None):
        if not key_name:
            key_name = "UNKNOWN"
        if not add_value:
            add_value = "UNKNOWN"
        if not self.list_value:
            d = self.data.setdefault(key_name, {self.nested_key_id_name: key_name,
                                                self.nested_key_data_name_1: add_value, "total": 0})
        else:
            d = self.data.setdefault(key_name, {self.nested_key_id_name: key_name,
                                                self.nested_key_data_name_1: [], "total": 0})
            d[self.nested_key_data_name_1].append(add_value)
        d["total"] += 1
        self.total += 1

    def get_sorted_list(self):
        items = []
        for pair in sorted(self.data.items(), key=lambda x: x[1]["total"], reverse=True):
            items.append(pair[1])
        return items

    def get_sorted_dict(self):
        od = OrderedDict()
        for d in self.get_sorted_list():
            od[d.get(self.ordered_dict_sort_key)] = d
        return od

    def get_top_dict(self):
        if len(self.data) == 0:
            return None
        else:
            d = max(self.data.values(), key=itemgetter("total"))
            d["ratio"] = d["total"] / self.total
            return d

    def to_dict(self) -> dict:
        return self.data


class TrackingBucketDual(TrackingBucket):
    def __init__(self, key_id_name: str, key_data_name_1: str, key_data_name_2: str, value_as_list=False,
                 unknown_overflow=True):
        self.nested_key_data_name_2 = key_data_name_2
        super().__init__(key_id_name, key_data_name_1, value_as_list, unknown_overflow)

    def add_item(self, key_name, add_value_1=None, add_value_2_list_append=None):
        if not key_name:
            key_name = "UNKNOWN"
        if not add_value_1:
            add_value_1 = "UNKNOWN"
        if not add_value_2_list_append:
            add_value_2_list_append = "UNKNOWN"
        if not self.list_value:
            d = self.data.setdefault(key_name, {self.nested_key_id_name: key_name,
                                                self.nested_key_data_name_1: add_value_1,
                                                self.nested_key_data_name_2: add_value_2_list_append,
                                                "total": 0})
        else:
            d = self.data.setdefault(key_name, {self.nested_key_id_name: key_name,
                                                self.nested_key_data_name_1: add_value_1,
                                                self.nested_key_data_name_2: [],
                                                "total": 0})
            d[self.nested_key_data_name_2].append(add_value_2_list_append)
        d["total"] += 1
        self.total += 1
