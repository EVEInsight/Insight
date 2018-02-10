import time
from multiprocessing.dummy import Pool as ThreadPool

import mysql.connector
import requests

from database.database_connection import *


class db_systems(object):
    """creates and imports system data if it does not yet exist"""

    def __init__(self, con, args):
        if not con.test_connection():
            raise ConnectionError
        self.con_ = con
        self.arguments = args
        self.endpoint_system_list = "https://esi.tech.ccp.is/latest/universe/systems/?datasource=tranquility"
        self.endpoint_system_info = "https://esi.tech.ccp.is/latest/universe/systems/{}/?datasource=tranquility&language=en-us"
        self.endpoint_constellation_list = "https://esi.tech.ccp.is/latest/universe/constellations/?datasource=tranquility"
        self.endpoint_constellation_info = "https://esi.tech.ccp.is/latest/universe/constellations/{}/?datasource=tranquility&language=en-us"
        self.endpoint_region_list = "https://esi.tech.ccp.is/latest/universe/regions/?datasource=tranquility"
        self.endpoint_region_info = "https://esi.tech.ccp.is/latest/universe/regions/{}/?datasource=tranquility&language=en-us"
        if not self.arguments.skip_gen:
            self.create_tables()
            self.import_system_ids()
            self.import_constellation_ids()
            self.import_region_ids()
            self.import_region_info()
            self.import_constellation_info()
            self.import_system_info()

    def create_tables(self):
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS regions("
                "region_id INT PRIMARY KEY NOT NULL,"
                "region_name VARCHAR(32) DEFAULT NULL,"
                "region_desc TEXT DEFAULT NULL)")
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS  constellations("
                "constellation_id INT PRIMARY KEY NOT NULL,"
                "constellation_name VARCHAR(32) DEFAULT NULL,"
                "c_pos_x DOUBLE PRECISION DEFAULT NULL,"
                "c_pos_y DOUBLE PRECISION DEFAULT NULL,"
                "c_pos_z DOUBLE PRECISION DEFAULT NULL,"
                "region_id_fk INT DEFAULT NULL,"
                "FOREIGN KEY (region_id_fk) REFERENCES regions(region_id))")
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS  systems("
                "system_id INT PRIMARY KEY NOT NULL,"
                "system_name VARCHAR(32) DEFAULT NULL,"
                "star_id INT DEFAULT NULL,"
                "s_pos_x DOUBLE PRECISION DEFAULT NULL,"
                "s_pos_y DOUBLE PRECISION DEFAULT NULL,"
                "s_pos_z DOUBLE PRECISION DEFAULT NULL,"
                "security_status FLOAT(5) DEFAULT NULL, "
                "security_class VARCHAR(5) DEFAULT NULL,"
                "constellation_id_fk INT DEFAULT NULL,"
                "FOREIGN KEY (constellation_id_fk) REFERENCES constellations(constellation_id))")
            connection.commit()
        except Exception as ex:
            print(ex)
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()

    def import_system_ids(self):
        resp = requests.get(self.endpoint_system_list, verify=True, timeout=10)
        if resp.status_code == 200:
            print("Got the system list")
            try:  # populate table with ids
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor()
                for id in resp.json():
                    cursor.execute("INSERT IGNORE INTO systems(system_id) VALUES (%s)",
                                   [id])
                connection.commit()
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
            raise ConnectionError("API ERROR: db_systems.import_system_ids api returned:{}".format(resp.status_code))

    def import_constellation_ids(self):
        resp = requests.get(self.endpoint_constellation_list, verify=True, timeout=10)
        if resp.status_code == 200:
            print("Got the constellation list")
            try:  # populate table with ids
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor()
                for id in resp.json():
                    cursor.execute("INSERT IGNORE INTO constellations(constellation_id) VALUES (%s)",
                                   [id])
                connection.commit()
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
            raise ConnectionError("API ERROR: db_systems.import_constellation_ids api returned:{}".format(resp.status_code))

    def import_region_ids(self):
        resp = requests.get(self.endpoint_region_list, verify=True, timeout=10)
        if resp.status_code == 200:
            print("Got the region list")
            try:  # populate table with ids
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor()
                for id in resp.json():
                    cursor.execute("INSERT IGNORE INTO regions(region_id) VALUES (%s)",
                                   [id])
                connection.commit()
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
            raise ConnectionError("API ERROR: db_systems.import_region_ids api returned:{}".format(resp.status_code))

    def import_system_info_api(self,system):
        try:
            resp = requests.get(self.endpoint_system_info.format(system["system_id"]), verify=True, timeout=10)
            if resp.status_code == 200:
                system["system_name"] = "\"{}\"".format(resp.json()["name"])
                system["star_id"] = resp.json()["star_id"]
                system["s_pos_x"] = resp.json()["position"]["x"]
                system["s_pos_y"] = resp.json()["position"]["y"]
                system["s_pos_z"] = resp.json()["position"]["z"]
                system["security_status"] = (resp.json()["security_status"])
                try:
                    system["security_class"] = "\"{}\"".format(resp.json()["security_class"]) #whs systems dont have class, ignore them
                except:
                    del system["security_class"]
                system["constellation_id_fk"] = resp.json()["constellation_id"]
            elif resp.status_code == 404:
                raise KeyError("API returned 404 on system id: {}\nCheck to make sure this system still exists or if the database is corrupted.".format(system["system_id"]))
            else:
                raise ConnectionError("api system info call got: {} from api".format(resp.status_code))
        except requests.exceptions.Timeout:
            print("API Timeout occurred, will retry")
            time.sleep(5)
            self.import_system_info_api(system)

    def import_system_info(self):
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM systems WHERE system_name IS NULL")
            system_list = cursor.fetchall()
            print("Downloading system info for {} systems from CCP API, this can take a few minutes".format(len(system_list)))
            pool = ThreadPool(4)
            pool.map(self.import_system_info_api,system_list)
            pool.close()
            pool.join()
            for i in system_list:
                cursor.execute("REPLACE INTO systems(%s) VALUES (%s)" % (",".join(i.keys()), ",".join(str(x) for x in i.values())))
                print("Imported: {}".format(i))
            connection.commit()
        except Exception as ex:
            print(ex)
            if connection:
                connection.rollback()
                connection.close()
            raise mysql.connector.DatabaseError
        finally:
            if connection:
                connection.close()

    def import_constellation_info_api(self, const):
        try:
            resp = requests.get(self.endpoint_constellation_info.format(const["constellation_id"]), verify=True, timeout=10)
            if resp.status_code == 200:
                const["constellation_name"] = "\"{}\"".format(resp.json()["name"])
                const["c_pos_x"] = resp.json()["position"]["x"]
                const["c_pos_y"] = resp.json()["position"]["y"]
                const["c_pos_z"] = resp.json()["position"]["z"]
                const["region_id_fk"] = resp.json()["region_id"]
            elif resp.status_code == 404:
                raise KeyError("API returned 404 on constellation id: {}\nCheck to make sure this constellation still exists or if the database is corrupted.".format(const["system_id"]))
            else:
                raise ConnectionError("api constellation info call got: {} from api".format(resp.status_code))
        except requests.exceptions.Timeout:
            print("API Timeout occurred, will retry")
            time.sleep(5)
            self.import_constellation_info_api(const)

    def import_constellation_info(self):
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM constellations WHERE constellation_name IS NULL")
            constellation_list = cursor.fetchall()
            print("Downloading constellation info for {} constellations from CCP API, this can take a few minutes".format(len(constellation_list)))
            pool = ThreadPool(4)
            pool.map(self.import_constellation_info_api, constellation_list)
            pool.close()
            pool.join()
            for i in constellation_list:
                cursor.execute("REPLACE INTO constellations(%s) VALUES (%s)" % (",".join(i.keys()), ",".join(str(x) for x in i.values())))
                print("Imported: {}".format(i))
            connection.commit()
        except Exception as ex:
            print(ex)
            if connection:
                connection.rollback()
                connection.close()
            raise mysql.connector.DatabaseError
        finally:
            if connection:
                connection.close()

    def import_region_info_api(self, region):
        try:
            resp = requests.get(self.endpoint_region_info.format(region["region_id"]), verify=True, timeout=10)
            if resp.status_code == 200:
                region["region_name"] = "\"{}\"".format(resp.json()["name"])
                try:
                    region["region_desc"] = resp.json()["description1"] #broken import needs fix
                except:
                    del region["region_desc"]
            elif resp.status_code == 404:
                raise KeyError("API returned 404 on region id: {}\nCheck to make sure this constellation still exists or if the database is corrupted.".format(region["system_id"]))
            else:
                raise ConnectionError("api region info call got: {} from api".format(resp.status_code))
        except requests.exceptions.Timeout:
            print("API Timeout occurred, will retry")
            time.sleep(5)
            self.import_region_info_api(region)

    def import_region_info(self):
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM regions WHERE region_name IS NULL")
            region_list = cursor.fetchall()
            print("Downloading region info for {} region from CCP API, this can take a few minutes".format(len(region_list)))
            pool = ThreadPool(4)
            pool.map(self.import_region_info_api, region_list)
            pool.close()
            pool.join()
            for i in region_list:
                cursor.execute("REPLACE INTO regions(%s) VALUES (%s)" % (",".join(i.keys()), ",".join(str(x) for x in i.values())))
                print("Imported: {}".format(i))
            connection.commit()
        except Exception as ex:
            print(ex)
            if connection:
                connection.rollback()
                connection.close()
            raise mysql.connector.DatabaseError
        finally:
            if connection:
                connection.close()