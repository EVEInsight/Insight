import math

import mysql.connector

from access.systems.pve_stats import pve_stats
from database.database_generation import *


class fa_systems(object):
    """provides access and search on systems cached in memory"""

    def __init__(self, con, cf_file, args):
        self.con_ = con
        self.config_file = cf_file
        self.arguments = args
        self.db_systems = db_systems(con=con, cf_file=cf_file, args=self.arguments)  # database instance
        self.system_list = []

        self.build_system_list()

        self.pve_stats = pve_stats(self)

    def build_system_list(self):
        connection = mysql.connector.connect(**self.con_.config())
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM systems LEFT JOIN constellations ON systems.constellation_id_fk = constellations.constellation_id LEFT JOIN regions ON constellations.region_id_fk=regions.region_id")
        self.system_list = cursor.fetchall()
        if connection:
            connection.close()
        print("Loaded system table with {} systems".format(len(self.system_list)))

    def display(self):
        for i in self.system_list:
            print(i)

    def ly_range(self, sys1, sys2):
        x1 = sys1["s_pos_x"]
        x2 = sys2["s_pos_x"]
        y1 = sys1["s_pos_y"]
        y2 = sys2["s_pos_y"]
        z1 = sys1["s_pos_z"]
        z2 = sys2["s_pos_z"]
        return (math.sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2) + pow(z2 - z1, 2)) / 9.4605284e15)

    def systems_in_range(self, sys1, distance):
        systems_in_range = []
        for i in self.system_list:
            if self.ly_range(sys1, i) < distance:
                systems_in_range.append(i)
        return (systems_in_range)

    def find(self, search_string):
        return ([sys for sys in self.system_list if sys['system_name'].lower().startswith(search_string.lower())])
