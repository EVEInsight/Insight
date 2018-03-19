import threading
import random
import mysql.connector
import string
from database.database_generation import *


class zk_thread(object):
    def __init__(self, con, cf_info, args):
        self.con_ = con
        self.config_file = cf_info
        self.arguments = args

        self.identifier = str(self.generate_identifier())
        self.zk_stream_url = str("https://redisq.zkillboard.com/listen.php?queueID={}".format(self.identifier))
        self.thread_zk_run = True

        if not self.arguments.disable_zKill:
            self.start_zk_pull_thread()
            self.start_thread_watcher()

    def generate_identifier(self):
        filename = 'zk_identifier.txt'  # move zk_identifier from config file to auto generated and unique
        try:
            with open(filename, 'r') as f:
                text = f.read()
                return text
        except FileNotFoundError:
            with open(filename, 'w') as f:
                random_s = ''.join(random.choice(string.ascii_lowercase) for x in range(8))
                f.write(random_s)
                return random_s

    def thread_zk_pull(self):
        def api_pull():
            try:
                resp = requests.get(self.zk_stream_url, verify=True,
                                    timeout=int(self.config_file['thread_zKill_pull']['timeout']))
                if resp.status_code == 200:
                    if (resp.json()['package'] == None):
                        pass
                    else:
                        insert_killmail(resp.json()['package'])
                        time.sleep(int(self.config_file['thread_zKill_pull']['delay_between_successful_pulls']))
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

    def thread_watcher(self):
        while self.thread_zk_run:
            if not self.thread_pull.is_alive():
                print("zk pull thread is not alive, restarting it!")
                self.start_zk_pull_thread()
            time.sleep(int(self.config_file['thread_zKill_pull']['thread_watcher_check_interval']))

    def start_zk_pull_thread(self):
        print("Starting zKill API pulling thread with identifier: '{}'".format(self.identifier))
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

    def kills_added_count(self, minutes=60):
        """returns number of new kills occurring in the last minutes"""
        assert isinstance(minutes, int)
        count = 0
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT COUNT(*) AS count FROM zk_kills WHERE killmail_time > (UTC_TIMESTAMP() - INTERVAL (%s) MINUTE);",
                [minutes])
            resp = cursor.fetchone()
            count = resp['count']
        except Exception as ex:
            print(ex)
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()
            return count
