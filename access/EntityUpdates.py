import threading
import traceback

import mysql.connector

from database.database_generation import *


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
                        insert['pilot_description'] = (resp.json()['description'].encode('utf-8', 'ignore')).decode(
                            'utf-8', 'ignore')
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
                        insert['description'] = (resp.json()['description'].encode('utf-8', 'ignore')).decode('utf-8',
                                                                                                              'ignore')
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

    def find(self, search_string):
        try:
            matches = {'pilots': None, 'corps': None, 'alliances': None}
            search_s = str(str(search_string) + "%")
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `alliances` WHERE `alliance_name` LIKE %s;",
                           [search_s])
            matches['alliances'] = cursor.fetchall()
            cursor.execute("SELECT * FROM `corps` WHERE `corp_name` LIKE %s;",
                           [search_s])
            matches['corps'] = cursor.fetchall()
            cursor.execute("SELECT * FROM `pilots` WHERE `pilot_name` LIKE %s;",
                           [search_s])
            matches['pilots'] = cursor.fetchall()
        except Exception as ex:
            print(ex)
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()
            return matches
