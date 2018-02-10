import math

import mysql.connector

from database.database_connection import *
from database.database_generation import *


class fa_systems(object):
    """provides access and search on systems cached in memory"""

    def __init__(self, con, args):
        self.con_ = con
        self.arguments = args
        self.db_systems = db_systems(con, args=self.arguments)  # database instance
        self.system_list = []

        self.build_system_list()

    def build_system_list(self):
        connection = mysql.connector.connect(**self.con_.config())
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM systems LEFT JOIN constellations ON systems.constellation_id_fk = constellations.constellation_id LEFT JOIN regions ON constellations.region_id_fk=regions.region_id")
        self.system_list = cursor.fetchall()
        if connection:
            connection.close()

    def display(self):
        for i in self.system_list:
            print(i)
    def ly_range(self,sys1,sys2):
        x1 = sys1["s_pos_x"]
        x2 = sys2["s_pos_x"]
        y1 = sys1["s_pos_y"]
        y2 = sys2["s_pos_y"]
        z1 = sys1["s_pos_z"]
        z2 = sys2["s_pos_z"]
        return(math.sqrt(pow(x2-x1, 2) + pow(y2-y1, 2) + pow(z2-z1, 2)) / 9.4605284e15)
    def systems_in_range(self,sys1,distance):
        systems_in_range = []
        for i in self.system_list:
            if self.ly_range(sys1, i) < distance:
                systems_in_range.append(i)
        return(systems_in_range)
    def find(self, search_string):
        return([sys for sys in self.system_list if sys['system_name'].lower().startswith(search_string.lower())])

class cap_info(object):
    def __init__(self, cf_info, args):
        self.config_file = cf_info
        self.arguments = args
        self.search_cap_type = self.make_search_cap_type()
        self.range = self.make_range_dict()
    def make_search_cap_type(self):
        return{
             "Avatar" : ["titans", "avatar", "erebus", "ragnarok", "levi", "leviathan", "tities", "vanquisher", "komodo", "bus", "tits"],
            "Aeon":["scs", "supercarriers", "supercaps", "nyx", "hel", "wyvern", "aeon", "Vendetta"],
            "Revelation": ["dreads", "dreadnoughts", "revelation", "moros", "naglfar", "phoenix"],
            "Archon": ["carriers", "faxs", "faxes" "archon", "thanatos", "nidhougor", "chimera", "apostle", "lif", "minokawa", "ninazu"],
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
