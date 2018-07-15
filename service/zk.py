import random
import time
import string
import requests
import queue
import datetime
import service
from sqlalchemy.orm import Session
import database.db_tables as dbRow
import statistics


class zk(object):
    def __init__(self, service_module):
        assert isinstance(service_module,service.ServiceModule)
        self.service = service_module

        self.rSession: requests.Session = self.make_session()
        identifier = str(self.generate_identifier())
        self.zk_stream_url = str("https://redisq.zkillboard.com/listen.php?queueID={}".format(identifier))
        self.run = True
        self.error_ids = []
        self.__km_preProcess = queue.Queue()  # raw json, before insertion to database
        self.__km_postProcess = queue.Queue()  # fully finished sqlalchemy objects with names resolved
        self.__error_km_json = queue.Queue()  # todo
        self.time_delay = queue.Queue()
        self.time_delay_sql = queue.Queue()

    def __add_delay(self, other_time):
        try:
            tn = datetime.datetime.now(datetime.timezone.utc)
            self.time_delay.put_nowait(((tn - other_time).total_seconds()) / 60)
        except Exception as ex:
            print(ex)

    def __add_sql_name_delay(self, other_time):
        try:
            self.time_delay_sql.put_nowait((datetime.datetime.utcnow() - other_time).total_seconds())
        except Exception as ex:
            print(ex)

    def avg_delay(self):
        values = []
        total = 0
        avg = 0
        try:
            while True:
                values.append(self.time_delay.get_nowait())
        except queue.Empty:
            try:
                total = len(values)
                avg = statistics.median(values)
            except:
                pass
        except Exception as ex:
            print(ex)
        finally:
            return (total, round(avg, 1), self.__avg_delay_sql())

    def __avg_delay_sql(self):
        values = []
        total = 0
        avg = 0
        try:
            while True:
                values.append(self.time_delay_sql.get_nowait())
        except queue.Empty:
            try:
                total = len(values)
                avg = sum(values) / total
            except:
                pass
        except Exception as ex:
            print(ex)
        finally:
            return (round(avg, 1))


    @staticmethod
    def generate_identifier():
        filename = 'zk_identifier.txt'
        try:
            with open(filename, 'r') as f:
                text = f.read()
                return text
        except FileNotFoundError:
            with open(filename, 'w') as f:
                random_s = ''.join(random.choice(string.ascii_lowercase) for x in range(8))
                f.write(random_s)
                return random_s

    def make_session(self):
        ses = requests.Session()
        ses.headers.update({
                               'User-Agent': "InsightDiscordKillfeeds https://github.com/Nathan-LS/Insight Maintainer:Nathan nathan@nathan-s.com"})
        return ses

    def __make_km(self, km_json):
        db:Session = self.service.get_session()
        __row = dbRow.tb_kills.make_row(km_json, self.service)
        if __row is not None:
            try:
                db.commit()
                self.__add_delay(__row.killmail_time)
                self.error_ids = dbRow.name_resolver.api_mass_name_resolve(self.service, error_ids=self.error_ids)
                return True
            except Exception as ex:
                db.rollback()
                print(ex)
                return False
            finally:
                db.close()
        else:
            db.close()
            return False

    def __debug_simulate(self):
        if self.service.cli_args.debug_km:
            self.service.channel_manager.post_message("Starting debug mode.\n"
                                "Starting KM ID: {}\n"
                                "Force time to now: {}\n"
                                "KM Limit: {}\n".format(str(self.service.cli_args.debug_km),str(self.service.cli_args.force_ctime),str(self.service.cli_args.debug_limit)))
            db:Session = self.service.get_session()
            try:
                results = db.query(dbRow.tb_kills).filter(dbRow.tb_kills.kill_id >=self.service.cli_args.debug_km).limit(self.service.cli_args.debug_limit).all()
                db.close()
                for km in results:
                    if self.service.cli_args.force_ctime:
                        km.killmail_time = datetime.datetime.utcnow()
                    self.__add_km_to_filter(km)
            except Exception as ex:
                print(ex)
            self.service.channel_manager.post_message("Debugging is now finished. Switching back to streaming live kms.")
            time.sleep(5)

    def thread_pull_km(self):
        print("Starting zk puller")
        self.__debug_simulate()
        while self.run:
            try:
                resp = self.rSession.get(self.zk_stream_url, verify=True, timeout=45)
                if resp.status_code == 200:
                    json_data = resp.json()['package']
                    if json_data == None:
                        pass
                    else:
                        self.__km_preProcess.put_nowait(json_data)
                else:
                    print("zk non 200 error code {}".format(resp.status_code))
                    time.sleep(.1)
            except Exception as ex:
                print(ex)
                time.sleep(.1)

    def __add_km_to_filter(self,km):
        try:
            assert isinstance(km,dbRow.tb_kills)
            km.loaded_time = datetime.datetime.utcnow()  # adjust for name resolve
            self.__km_postProcess.put_nowait(km)
        except Exception as ex:
            print(ex)

    def thread_process_json(self):
        print('Starting zk data processor')
        while True:
            try:
                json_data = self.__km_preProcess.get(block=True)
                pull_start_time = datetime.datetime.utcnow()
                if self.__make_km(json_data):
                    __km = dbRow.tb_kills.get_row(json_data, self.service)
                    self.service.get_session().close()
                    self.__add_km_to_filter(__km)
                    self.__add_sql_name_delay(pull_start_time)
            except Exception as ex:
                print(ex)

    def thread_filters(self):
        print("Starting zk filter pass")
        while True:
            try:
                self.service.channel_manager.send_km(self.__km_postProcess.get(block=True))
            except Exception as ex:
                print(ex)
