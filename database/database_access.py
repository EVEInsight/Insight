import datetime
import json
import math
import threading
import traceback

import mysql.connector

from database.database_connection import *
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

    def thread_watcher(self):
        while self.thread_pve_pull_run:
            if not self.thread_pull.is_alive():
                print("PvE stats thread is not alive, restarting it!")
                self.start_api_pull_thread()
            time.sleep(int(self.systems.config_file['thread_pve_pull']['thread_watcher_check_interval']))
    def start_api_pull_thread(self):
        self.thread_pull = threading.Thread(target=self.thread_pve_pull)
        self.thread_pull.start()

    def start_thread_watcher(self):
        self.thread_watcher = threading.Thread(target=self.thread_watcher)
        self.thread_watcher.start()

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


class zk_thread(object):
    def __init__(self, con, cf_info, args):
        self.con_ = con
        self.config_file = cf_info
        self.arguments = args
        self.en_updates = EntityUpdates(con=con, cf_info=cf_info, args=args)

        self.zk_stream_url = str("https://redisq.zkillboard.com/listen.php?queueID={}".format(
            self.config_file['thread_zKill_pull']['zkill_unique_identifier']))
        self.thread_zk_run = True

        if not self.arguments.disable_zKill:
            self.start_zk_pull_thread()
            self.start_thread_watcher()

    def thread_zk_pull(self):
        def api_pull():
            try:
                resp = requests.get(self.zk_stream_url, verify=True,
                                    timeout=int(self.config_file['thread_zKill_pull']['timeout']))
                if resp.status_code == 200:
                    if (resp.json()['package'] == None):
                        time.sleep(int(self.config_file['thread_zKill_pull']['delay_when_no_kills']))
                    else:
                        insert_killmail(resp.json()['package'])
                else:
                    print("zk non 200 error code {}".format(resp.status_code))
                    time.sleep(int(self.config_file['thread_zKill_pull']['delay_between_non200_response']))
            except requests.exceptions.RequestException as ex:
                print(ex)
                time.sleep(int(self.config_file['thread_zKill_pull']['delay_between_response_exception_api']))

        def db_insert_header(data, cur):
            insert = {}
            insert['killmail_id'] = data['killmail']['killmail_id']
            insert['killmail_time'] = data['killmail']['killmail_time']
            insert['system_id'] = data['killmail']['solar_system_id']
            insert['fittedValue'] = data['zkb']['fittedValue']
            insert['totalValue'] = data['zkb']['totalValue']
            cur.execute(
                "INSERT INTO `zk_kills` (`killmail_id`, `killmail_time`, `system_id`, `fittedValue`, `totalValue`) VALUES (%s,%s,%s,%s,%s);",
                [insert['killmail_id'], insert['killmail_time'], insert['system_id'], insert['fittedValue'],
                 insert['totalValue']])

        def db_insert_involved(data, kill_id, cur, victim=False):
            insert = {}
            insert['kill_id'] = kill_id
            if 'character_id' in data:
                insert['character_id'] = data['character_id']
            if 'corporation_id' in data:
                insert['corporation_id'] = data['corporation_id']
            if 'alliance_id' in data:
                insert['alliance_id'] = data['alliance_id']
            if 'faction_id' in data:
                insert['faction_id'] = data['faction_id']

            if 'damage_done' in data:
                insert['damage'] = data['damage_done']
            elif 'damage_taken' in data:
                insert['damage'] = data['damage_taken']

            if 'ship_type_id' in data:
                insert['ship_type_id'] = data['ship_type_id']
            if 'weapon_type_id' in data:
                insert['weapon_type_id'] = data['weapon_type_id']
            if 'final_blow' in data:
                insert['is_final_blow'] = data['final_blow']
            insert['is_victim'] = victim

            cur.execute("INSERT INTO zk_involved(%s) VALUES (%s)" % (
                ",".join(insert.keys()), ",".join(str(x) for x in insert.values())))

        def insert_killmail(package):
            try:
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor(dictionary=True)
                kill_id = package['killmail']['killmail_id']
                db_insert_header(package, cursor)
                db_insert_involved(package['killmail']['victim'], kill_id, cursor, victim=True)
                for i in package['killmail']['attackers']:
                    db_insert_involved(i, kill_id, cursor)
                connection.commit()
            except Exception as ex:
                print(ex)
                if connection:
                    connection.rollback()
                    connection.close()
            finally:
                if connection:
                    connection.close()

        while self.thread_zk_run:
            api_pull()
            time.sleep(int(self.config_file['thread_zKill_pull']['delay_between_successful_pulls']))

    def thread_watcher(self):
        while self.thread_zk_run:
            if not self.thread_pull.is_alive():
                print("zk pull thread is not alive, restarting it!")
                self.start_zk_pull_thread()
            time.sleep(int(self.config_file['thread_zKill_pull']['thread_watcher_check_interval']))

    def start_zk_pull_thread(self):
        print("Starting zKill API pulling thread")
        self.thread_pull = threading.Thread(target=self.thread_zk_pull)
        self.thread_pull.start()

    def start_thread_watcher(self):
        self.thread_watcher = threading.Thread(target=self.thread_watcher)
        self.thread_watcher.start()

    def pilot_name_to_ships(self, pilot_name):
        result = None
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM pilots_to_kms WHERE pilot_name = %s ORDER BY killmail_time DESC LIMIT 1;",
                           [str(pilot_name)])
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


class EntityUpdates(object):
    def __init__(self, con, cf_info, args):
        self.con_ = con
        self.config_file = cf_info
        self.arguments = args

        self.thread_Updates_run = True
        if not self.arguments.disable_EntityUpdates:
            self.start_update_threads()
            self.start_thread_watcher()

    def api_pilot_thread(self):
        def insert_data(pilot_id, resp):
            try:
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor(dictionary=True)
                sql = "UPDATE pilots SET {} WHERE pilot_id=%s".format(', '.join('{}=%s'.format(key) for key in resp))
                cursor.execute(sql, [str(i) for i in resp.values()] + [pilot_id])
                connection.commit()
            except Exception as ex:
                print(ex)
                if connection:
                    connection.rollback()
                    connection.close()
            finally:
                if connection:
                    connection.close()

        def api_pull(val):
            try:
                resp = requests.get(
                    "https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(val['pilot_id']),
                    verify=True,
                    timeout=int(self.config_file['thread_EntityUpdates']['api_request_timeout']))
                if resp.status_code == 200:
                    insert = {}
                    insert['pilot_name'] = resp.json()['name']
                    insert['corporation_id'] = resp.json()['corporation_id']
                    insert['pilot_birthday'] = resp.json()['birthday']
                    insert['gender'] = resp.json()['gender']
                    insert['race_id'] = resp.json()['race_id']
                    insert['bloodline_id'] = resp.json()['bloodline_id']

                    if 'description' in resp.json():
                        insert['pilot_description'] = resp.json()['description']
                    if 'ancestry_id' in resp.json():
                        insert['ancestry_id'] = resp.json()['ancestry_id']
                    if 'security_status' in resp.json():
                        insert['security_status'] = resp.json()['security_status']
                    if 'faction_id' in resp.json():
                        insert['faction_id'] = resp.json()['faction_id']

                    insert_data(val['pilot_id'], insert)
                else:
                    print("api_pilot_thread non 200 error code {} on pilot_id: {}".format(resp.status_code,
                                                                                          val['pilot_id']))
            except requests.exceptions.RequestException as ex:
                print(ex)

        def findValsUpdate():
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM pilots WHERE pilots.pilot_name IS NULL;")
            vals = cursor.fetchall()
            connection.close()
            return vals

        while self.thread_Updates_run:
            pool = ThreadPool(int(self.config_file['thread_EntityUpdates']['threads_per_pool']))
            try:
                updateIDs = findValsUpdate()
                pool.map(api_pull, updateIDs)
                pool.close()
                pool.join()
                if len(updateIDs) != 0:
                    print("Updated pilot information for {} pilots".format(len(updateIDs)))
                time.sleep(int(self.config_file['thread_EntityUpdates']['pool_secondsWaitAfterSuccessful_Pull']))
            except:
                traceback.print_exc()
                pool.close()
                pool.join()
                time.sleep(int(self.config_file['thread_EntityUpdates']['pool_secondsWaitAfterException_Pull']))
                exit()

    def api_corp_thread(self):
        def insert_data(corp_id, resp):
            try:
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor(dictionary=True)
                sql = "UPDATE corps SET {} WHERE corp_id=%s".format(', '.join('{}=%s'.format(key) for key in resp))
                cursor.execute(sql, [str(i) for i in resp.values()] + [corp_id])
                connection.commit()
            except Exception as ex:
                print(ex)
                if connection:
                    connection.rollback()
                    connection.close()
            finally:
                if connection:
                    connection.close()

        def api_pull(val):
            try:
                resp = requests.get(
                    "https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(val['corp_id']),
                    verify=True,
                    timeout=int(self.config_file['thread_EntityUpdates']['api_request_timeout']))
                if resp.status_code == 200:
                    insert = {}
                    insert['corp_name'] = resp.json()['name']
                    insert['corp_ticker'] = resp.json()['ticker']
                    insert['member_count'] = resp.json()['member_count']
                    insert['ceo_id'] = resp.json()['ceo_id']
                    insert['tax_rate'] = resp.json()['tax_rate']
                    insert['creator_id'] = resp.json()['creator_id']

                    if 'alliance_id' in resp.json():
                        insert['alliance_id'] = resp.json()['alliance_id']
                    if 'description' in resp.json():
                        insert['description'] = resp.json()['description']
                    if 'date_founded' in resp.json():
                        insert['date_founded'] = resp.json()['date_founded']
                    if 'url' in resp.json():
                        insert['url'] = resp.json()['url']
                    if 'faction_id' in resp.json():
                        insert['faction_id'] = resp.json()['faction_id']
                    if 'home_station_id' in resp.json():
                        insert['home_station_id'] = resp.json()['home_station_id']
                    if 'shares' in resp.json():
                        insert['shares'] = resp.json()['shares']

                    insert_data(val['corp_id'], insert)
                else:
                    print(
                        "api_corp_thread non 200 error code {} on corp_id: {}".format(resp.status_code, val['corp_id']))
            except requests.exceptions.RequestException as ex:
                print(ex)

        def findValsUpdate():
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM corps WHERE corps.corp_name IS NULL;")
            vals = cursor.fetchall()
            connection.close()
            return vals

        while self.thread_Updates_run:
            pool = ThreadPool(int(self.config_file['thread_EntityUpdates']['threads_per_pool']))
            try:
                updateIDs = findValsUpdate()
                pool.map(api_pull, updateIDs)
                pool.close()
                pool.join()
                if len(updateIDs) != 0:
                    print("Updated corp information for {} corps".format(len(updateIDs)))
                time.sleep(int(self.config_file['thread_EntityUpdates']['pool_secondsWaitAfterSuccessful_Pull']))
            except:
                traceback.print_exc()
                pool.close()
                pool.join()
                time.sleep(int(self.config_file['thread_EntityUpdates']['pool_secondsWaitAfterException_Pull']))
                exit()

    def api_alliance_thread(self):
        def insert_data(alliance_id, resp):
            try:
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor(dictionary=True)
                sql = "UPDATE alliances SET {} WHERE alliance_id=%s".format(
                    ', '.join('{}=%s'.format(key) for key in resp))
                cursor.execute(sql, [str(i) for i in resp.values()] + [alliance_id])
                connection.commit()
            except Exception as ex:
                print(ex)
                if connection:
                    connection.rollback()
                    connection.close()
            finally:
                if connection:
                    connection.close()

        def api_pull(val):
            try:
                resp = requests.get(
                    "https://esi.tech.ccp.is/latest/alliances/{}/?datasource=tranquility".format(val['alliance_id']),
                    verify=True,
                    timeout=int(self.config_file['thread_EntityUpdates']['api_request_timeout']))
                if resp.status_code == 200:
                    insert = {}
                    insert['alliance_name'] = resp.json()['name']
                    insert['creator_id'] = resp.json()['creator_id']
                    insert['creator_corporation_id'] = resp.json()['creator_corporation_id']
                    insert['ticker'] = resp.json()['ticker']
                    insert['date_founded'] = resp.json()['date_founded']

                    if 'faction_id' in resp.json():
                        insert['faction_id'] = resp.json()['faction_id']
                    if 'executor_corporation_id' in resp.json():
                        insert['executor_corporation_id'] = resp.json()['executor_corporation_id']

                    insert_data(val['alliance_id'], insert)
                else:
                    print("api_alliance_thread non 200 error code {} on alliance_id".format(resp.status_code,
                                                                                            val['alliance_id']))
            except requests.exceptions.RequestException as ex:
                print(ex)

        def findValsUpdate():
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM alliances WHERE alliances.alliance_name IS NULL;")
            vals = cursor.fetchall()
            connection.close()
            return vals

        while self.thread_Updates_run:
            pool = ThreadPool(int(self.config_file['thread_EntityUpdates']['threads_per_pool']))
            try:
                updateIDs = findValsUpdate()
                pool.map(api_pull, updateIDs)
                pool.close()
                pool.join()
                if len(updateIDs) != 0:
                    print("Updated alliance information for {} alliances".format(len(updateIDs)))
                time.sleep(int(self.config_file['thread_EntityUpdates']['pool_secondsWaitAfterSuccessful_Pull']))
            except:
                traceback.print_exc()
                pool.close()
                pool.join()
                time.sleep(int(self.config_file['thread_EntityUpdates']['pool_secondsWaitAfterException_Pull']))
                exit()

    def thread_watcher(self):
        while self.thread_Updates_run:
            if not self.pilot_info_thread.is_alive():
                print("Pilots thread is not alive, restarting it!")
                self.pilot_info_thread.join()
                self.start_pilot_thread()
            if not self.corp_info_thread.is_alive():
                print("Corps thread is not alive, restarting it!")
                self.corp_info_thread.join()
                self.start_corps_thread()
            if not self.alliance_info_thread.is_alive():
                print("Alliances thread is not alive, restarting it!")
                self.alliance_info_thread.join()
                self.start_alliances_thread()
            time.sleep(int(self.config_file['thread_EntityUpdates']['thread_watcher_check_interval']))

    def start_pilot_thread(self):
        self.pilot_info_thread = threading.Thread(target=self.api_pilot_thread)
        print("Starting pilot updates thread")
        self.pilot_info_thread.start()

    def start_corps_thread(self):
        self.corp_info_thread = threading.Thread(target=self.api_corp_thread)
        print("Starting corp updates thread")
        self.corp_info_thread.start()

    def start_alliances_thread(self):
        self.alliance_info_thread = threading.Thread(target=self.api_alliance_thread)
        print("Starting alliance updates thread")
        self.alliance_info_thread.start()

    def start_update_threads(self):
        self.start_pilot_thread()
        self.start_corps_thread()
        self.start_alliances_thread()

    def start_thread_watcher(self):
        self.thread_watcher = threading.Thread(target=self.thread_watcher)
        print("Starting EntityUpdate thread watcher")
        self.thread_watcher.start()
