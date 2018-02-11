import datetime
import json
import math
import threading

import mysql.connector

from database.database_connection import *
from database.database_generation import *


class fa_systems(object):
    """provides access and search on systems cached in memory"""

    def __init__(self, con, cf_file, args):
        self.con_ = con
        self.config_file = cf_file
        self.arguments = args
        self.db_systems = db_systems(con, args=self.arguments)  # database instance
        self.system_list = []

        self.build_system_list()

        self.pve_stats = pve_stats(self)

    def build_system_list(self):
        connection = mysql.connector.connect(**self.con_.config())
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM systems LEFT JOIN constellations ON systems.constellation_id_fk = constellations.constellation_id LEFT JOIN regions ON constellations.region_id_fk=regions.region_id")
        self.system_list = cursor.fetchall()
        if connection:
            connection.close()
        print("Loaded system table with {} systems".format(len(self.system_list)))

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
            "Aeon": ["scs", "supers", "supercarriers", "supercaps", "nyx", "hel", "wyvern", "aeon", "Vendetta"],
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

class pve_stats(object):
    def __init__(self, systems_l):
        if not isinstance(systems_l, fa_systems):
            raise TypeError
        self.systems = systems_l

        self.expires = None
        self.last_updated = None
        self.initial_times()

        self.endpoint_system_kills = "https://esi.tech.ccp.is/latest/universe/system_kills/?datasource=tranquility"
        self.thread_pve_pull_run = True
        self.start_api_pull_thread()

    def thread_pve_pull(self):
        def api_import():
            system_ids_master = [i["system_id"] for i in self.systems.system_list]
            try:
                resp = requests.get(self.endpoint_system_kills, verify=True, timeout=10)
                if resp.status_code == 200:
                    request_expires = datetime.datetime.strptime(resp.headers['Expires'], '%a, %d %b %Y %H:%M:%S %Z')
                    request_lu = datetime.datetime.strptime(resp.headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S %Z')
                    request_date_accessed = datetime.datetime.strptime(resp.headers['Date'], '%a, %d %b %Y %H:%M:%S %Z')
                    print("Got system kills\nRequest Date: {}\nLast Updated: {}\nExpires: {}".format(
                        request_date_accessed,
                        request_lu,
                        request_expires))
                    if datetime.datetime.utcnow() > self.expires:
                        try:
                            connection = mysql.connector.connect(**self.systems.con_.config())
                            cursor = connection.cursor()
                            cursor.execute(
                                "INSERT INTO api_raw_system_kills(last_modified,expires,retrieval,raw_json) VALUES (%s,%s,%s,%s)",
                                [request_lu, request_expires, request_date_accessed, json.dumps(resp.json())])
                            system_ids_nonzero = []
                            for i in resp.json():
                                cursor.execute(
                                    "INSERT INTO pve_stats(date,system_fk,ship_kills,npc_kills,pod_kills) VALUES (%s,%s,%s,%s,%s)",
                                    [request_lu, i['system_id'], i['ship_kills'], i['npc_kills'], i['pod_kills']])
                                system_ids_nonzero.append(i['system_id'])
                            for id in (list(set(system_ids_master) - set(system_ids_nonzero))):
                                cursor.execute(
                                    "INSERT INTO pve_stats(date,system_fk,ship_kills,npc_kills,pod_kills) VALUES (%s,%s,%s,%s,%s)",
                                    [request_lu, id, 0, 0, 0])
                            connection.commit()
                            self.last_updated = request_lu
                            self.expires = request_expires
                        except mysql.connector.IntegrityError as ex:
                            print(ex)
                            if connection:
                                connection.rollback()
                                connection.close()
                        except Exception as ex:
                            print(ex)
                            if connection:
                                connection.rollback()
                                connection.close()
                            raise mysql.connector.DatabaseError
                        finally:
                            if connection:
                                connection.close()
                else:
                    sleep_time = float(self.systems.config_file['thread_pve_pull']['retry_after_non200'])
                    print(
                        "API ERROR: pve_stats returned {} -Waiting {}s before requesting api again".format(
                            resp.status_code, sleep_time))
                    time.sleep(sleep_time)
            except requests.exceptions.RequestException as ex:
                sleep_time = float(self.systems.config_file['thread_pve_pull']['retry_after_requests_ex'])
                print("thread_pve_pull requests exception: {} --waiting {}s to retry".format(ex, sleep_time))
                time.sleep(sleep_time)

        while self.thread_pve_pull_run:
            try:
                dif = ((self.expires - datetime.datetime.utcnow()).total_seconds() + float(
                    self.systems.config_file['thread_pve_pull']['added_offset']))
                if dif < 0:
                    raise ValueError
                print("System kills API import thread sleeping for {}s {} is next update".format(dif, self.expires))
                time.sleep(dif)
                api_import()
            except ValueError:
                time.sleep(10)
                api_import()

    def initial_times(self):
        try:
            connection = mysql.connector.connect(**self.systems.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM api_raw_system_kills WHERE last_modified=(SELECT MAX(last_modified) FROM api_raw_system_kills)")
            result = cursor.fetchone()
            if result is None:
                self.last_updated = datetime.datetime.utcnow()
                self.expires = datetime.datetime.utcnow()
            else:
                self.last_updated = result['last_modified']
                self.expires = result['expires']
        except Exception as ex:
            print(ex)
            if connection:
                connection.rollback()
                connection.close()
        finally:
            if connection:
                connection.close()

    def start_api_pull_thread(self):
        thread_1 = threading.Thread(target=self.thread_pve_pull)
        thread_1.start()

    def npc_kills_last_hour(self, system):
        result = {}
        try:
            connection = mysql.connector.connect(**self.systems.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM pve_stats WHERE date=(SELECT MAX(date) FROM pve_stats) AND system_fk = %s",
                (system['system_id'],))
            result = cursor.fetchone()
        except Exception as ex:
            print(ex)
            if connection:
                connection.rollback()
                connection.close()
        finally:
            if connection:
                connection.close()
            return result

    def npc_delta(self, system):
        result_d = {}
        try:
            connection = mysql.connector.connect(**self.systems.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM pve_stats WHERE system_fk=%s ORDER BY date DESC LIMIT 2", (system['system_id'],))
            result = cursor.fetchall()
            result_d['npc_kills'] = result[0]['npc_kills'] - result[1]['npc_kills']
            result_d['ship_kills'] = result[0]['ship_kills'] - result[1]['ship_kills']
            result_d['pod_kills'] = result[0]['pod_kills'] - result[1]['pod_kills']
            result_d['time0'] = result[0]['date']
            result_d['time1'] = result[1]['date']
        except Exception as ex:
            print(ex)
            if connection:
                connection.rollback()
                connection.close()
        finally:
            if connection:
                connection.close()
            return result_d
