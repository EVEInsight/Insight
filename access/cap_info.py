class cap_info(object):
    def __init__(self, cf_info, args):
        self.config_file = cf_info
        self.arguments = args
        self.search_cap_type = self.make_search_cap_type()
        self.range = self.make_range_dict()

        self.super_ids = [int(i) for i in self.config_file['eve_settings']['super_group_ids'].split('\n')]
        self.capital_ids = [int(i) for i in self.config_file['eve_settings']['capital_group_ids'].split('\n')]
        self.blops_ids = [int(i) for i in self.config_file['eve_settings']['blops_group_ids'].split('\n')]

        self.sorted_by_value = []
        self.make_sorted_groupids()

    def make_search_cap_type(self):
        return {
            "Avatar": ["titans", "avatar", "erebus", "ragnarok", "levi", "leviathan", "tities", "vanquisher", "komodo",
                       "bus", "tits"],
            "Aeon": ["scs", "supers", "supercarriers", "supercaps", "nyx", "hel", "wyvern", "aeon", "Vendetta"],
            "Revelation": ["dreads", "dreadnoughts", "revelation", "moros", "naglfar", "phoenix"],
            "Archon": ["carriers", "faxs", "faxes" "archon", "thanatos", "nidhougor", "chimera", "apostle", "lif",
                       "minokawa", "ninazu"],
            "Redeemer": ["blops", "bs", "blackops", "redeemer", "sin", "panther", "widow", "marshal"],
            "Ark": ["jfs", "freighters", "jumps", "jumpfreighters", "ark", "anshar", "nomad", "rhea"],
            "Rorqual": ["rorqs", "rorquals"]}

    def make_range_dict(self):
        return {"Titans": {"JDC4": self.config_file["eve_settings"]["titan_range_4"],
                           "JDC5": self.config_file["eve_settings"]["titan_range_5"]},
                "Supercarriers": {"JDC4": self.config_file["eve_settings"]["super_range_4"],
                                  "JDC5": self.config_file["eve_settings"]["super_range_5"]},
                "Carriers": {"JDC4": self.config_file["eve_settings"]["carrier_range_4"],
                             "JDC5": self.config_file["eve_settings"]["carrier_range_5"]},
                "Dreads": {"JDC4": self.config_file["eve_settings"]["dread_range_4"],
                           "JDC5": self.config_file["eve_settings"]["dread_range_5"]},
                "JumpFreighters": {"JDC4": self.config_file["eve_settings"]["jf_range_4"],
                                   "JDC5": self.config_file["eve_settings"]["jf_range_5"]},
                "Blops": {"JDC4": self.config_file["eve_settings"]["blops_range_4"],
                          "JDC5": self.config_file["eve_settings"]["blops_range_5"]}
                }

    def make_sorted_groupids(self):
        self.sorted_by_value.extend(self.super_ids)
        self.sorted_by_value.extend(self.capital_ids)
        self.sorted_by_value.extend(self.blops_ids)

    def return_jump_range(self, ship):
        if ship == "Avatar":
            return float(self.config_file["eve_settings"]["titan_range_5"])
        elif ship == "Aeon":
            return float(self.config_file["eve_settings"]["super_range_5"])
        elif ship == "Archon":
            return float(self.config_file["eve_settings"]["carrier_range_5"])
        elif ship == "Revelation":
            return float(self.config_file["eve_settings"]["dread_range_5"])
        elif ship == "Redeemer":
            return float(self.config_file["eve_settings"]["blops_range_5"])
        elif ship == "Ark":
            return float(self.config_file["eve_settings"]["jf_range_5"])
        else:  # todo add rorqual jump range info
            return None

    def is_super(self, id):
        if int(id) in self.super_ids:
            return True
        else:
            return False

    def is_capital(self, id):
        if int(id) in self.capital_ids:
            return True
        else:
            return False

    def is_blops(self, id):
        if int(id) in self.blops_ids:
            return True
        else:
            return False

    def groups_by_value(self):
        """returns a list of group ids sorted by value titans > supercarriers and so forth"""
        return self.sorted_by_value
