import datetime
import json
import threading

import mysql.connector

import access.systems.systems
from database.database_generation import *


class pve_stats(object):
    def __init__(self, systems_l):
        if not isinstance(systems_l, access.systems.systems.fa_systems):
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
