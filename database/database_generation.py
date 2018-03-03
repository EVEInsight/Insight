import time
from multiprocessing.dummy import Pool as ThreadPool

import mysql.connector
import requests


class db_systems(object):
    """creates and imports system data if it does not yet exist"""

    def __init__(self, con, cf_file, args):
        if not con.test_connection():
            raise ConnectionError
        self.con_ = con
        self.arguments = args
        self.config_file = cf_file
        self.endpoint_system_list = "https://esi.tech.ccp.is/latest/universe/systems/?datasource=tranquility"
        self.endpoint_system_info = "https://esi.tech.ccp.is/latest/universe/systems/{}/?datasource=tranquility&language=en-us"
        self.endpoint_constellation_list = "https://esi.tech.ccp.is/latest/universe/constellations/?datasource=tranquility"
        self.endpoint_constellation_info = "https://esi.tech.ccp.is/latest/universe/constellations/{}/?datasource=tranquility&language=en-us"
        self.endpoint_region_list = "https://esi.tech.ccp.is/latest/universe/regions/?datasource=tranquility"
        self.endpoint_region_info = "https://esi.tech.ccp.is/latest/universe/regions/{}/?datasource=tranquility&language=en-us"
        self.endpoint_category_list = "https://esi.tech.ccp.is/latest/universe/categories/?datasource=tranquility"
        self.endpoint_item_groups_list = "https://esi.tech.ccp.is/latest/universe/groups/?datasource=tranquility"
        self.endpoint_group_info = "https://esi.tech.ccp.is/latest/universe/groups/{}/?datasource=tranquility&language=en-us"
        self.endpoint_category_info = "https://esi.tech.ccp.is/latest/universe/categories/{}/?datasource=tranquility&language=en-us"
        self.endpoint_type_info = "https://esi.tech.ccp.is/latest/universe/types/{}/?datasource=tranquility&language=en-us"

        if not self.arguments.skip_gen:
            self.create_tables()
            self.import_system_ids()
            self.import_constellation_ids()
            self.import_region_ids()

            self.import_region_info()
            self.import_constellation_info()
            self.import_system_info()

            self.import_item_category_ids()
            # self.import_item_group_ids()
            self.import_item_category_info()
            self.import_item_group_info()
            self.import_type_ship_info()

    def create_tables(self):
        print(
            "The application no longer handles creation of database tables. Please use your MySQL client to import the SQL Schema located under /SQL/InitialCreation.sql")

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

    def import_system_info_api(self, system):
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
            pool = ThreadPool(int(self.config_file['api_import']['threads']))
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
            pool = ThreadPool(int(self.config_file['api_import']['threads']))
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
            pool = ThreadPool(int(self.config_file['api_import']['threads']))
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

    def import_item_category_ids(self):
        resp = requests.get(self.endpoint_category_list, verify=True, timeout=10)
        if resp.status_code == 200:
            print("Got the item category list")
            try:  # populate table with ids
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor()
                for id in resp.json():
                    cursor.execute("INSERT IGNORE INTO item_category(category_id) VALUES (%s)",
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
            raise ConnectionError("API ERROR: db_systems item_category_list api returned:{}".format(resp.status_code))

    # def import_item_group_ids(self):
    #     resp = requests.get(self.endpoint_item_groups_list, verify=True, timeout=10)
    #     if resp.status_code == 200:
    #         print("Got the item group list")
    #         try:  # populate table with ids
    #             connection = mysql.connector.connect(**self.con_.config())
    #             cursor = connection.cursor()
    #             for id in resp.json():
    #                 cursor.execute("INSERT IGNORE INTO item_groups(group_id) VALUES (%s)",
    #                                [id])
    #             connection.commit()
    #         except Exception as ex:
    #             print(ex)
    #             if connection:
    #                 connection.rollback()
    #                 connection.close()
    #             raise mysql.connector.DatabaseError
    #         finally:
    #             if connection:
    #                 connection.close()
    #     else:
    #         raise ConnectionError("API ERROR: db_systems item_group_list api returned:{}".format(resp.status_code))

    def import_item_category_info(self):
        def importFromAPI(item):
            try:
                resp = requests.get(self.endpoint_category_info.format(item["category_id"]), verify=True, timeout=10)
                if resp.status_code == 200:
                    item['category_name'] = "\"{}\"".format(resp.json()["name"])
                    item['category_published'] = resp.json()['published']
                    item['groups'] = resp.json()['groups']
                elif resp.status_code == 404:
                    raise KeyError(
                        "API returned 404 on category_id: {}\nCheck to make sure this entry still exists or if the database is corrupted.".format(
                            item["category_id"]))
                else:
                    raise ConnectionError("api category_id info call got: {} from api".format(resp.status_code))
            except requests.exceptions.Timeout:
                print("API Timeout occurred, will retry")
                time.sleep(5)
                importFromAPI(item)

        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM item_category WHERE category_name IS NULL")
            to_update = cursor.fetchall()
            print("Downloading item category info for {} groups from CCP API, this can take a few minutes".format(
                len(to_update)))
            pool = ThreadPool(int(self.config_file['api_import']['threads']))
            pool.map(importFromAPI, to_update)
            pool.close()
            pool.join()
            for i in to_update:
                groups_c = i['groups']
                del i['groups']
                cursor.execute("REPLACE INTO item_category(%s) VALUES (%s)" % (
                    ",".join(i.keys()), ",".join(str(x) for x in i.values())))
                for val in groups_c:
                    cursor.execute("INSERT IGNORE item_groups(group_id, item_category_fk) VALUES (%s,%s)",
                                   [val, i['category_id']])
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

    def import_item_group_info(self):
        def importFromAPI(item):
            try:
                resp = requests.get(self.endpoint_group_info.format(item["group_id"]), verify=True, timeout=10)
                if resp.status_code == 200:
                    item['group_name'] = "\"{}\"".format(resp.json()["name"])
                    item['published'] = resp.json()['published']
                    item['item_category_fk'] = resp.json()['category_id']
                    item['types'] = resp.json()['types']
                elif resp.status_code == 404:
                    raise KeyError(
                        "API returned 404 on group id: {}\nCheck to make sure this entry still exists or if the database is corrupted.".format(
                            item["group_id"]))
                else:
                    raise ConnectionError("api group id info call got: {} from api".format(resp.status_code))
            except requests.exceptions.Timeout:
                print("API Timeout occurred, will retry")
                time.sleep(5)
                importFromAPI(item)

        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM item_groups WHERE group_name IS NULL")
            to_update = cursor.fetchall()
            print("Downloading item group info for {} groups from CCP API, this can take a few minutes".format(
                len(to_update)))
            pool = ThreadPool(int(self.config_file['api_import']['threads']))
            pool.map(importFromAPI, to_update)
            pool.close()
            pool.join()
            for i in to_update:
                types_c = i['types']
                del i['types']
                cursor.execute("REPLACE INTO item_groups(%s) VALUES (%s)" % (
                    ",".join(i.keys()), ",".join(str(x) for x in i.values())))
                for val in types_c:
                    cursor.execute("INSERT IGNORE item_types(type_id, group_id_fk) VALUES (%s,%s)",
                                   [val, i['group_id']])
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

    def import_type_ship_info(self):
        def importFromAPI(item):
            try:
                resp = requests.get(self.endpoint_type_info.format(item["type_id"]), verify=True, timeout=10)
                if resp.status_code == 200:
                    item['type_name'] = "\"{}\"".format(resp.json()['name'])
                    item['type_published'] = resp.json()['published']
                    # item['type_description'] = str(resp.json()['description']) #todo fix import error for description
                    item['group_id_fk'] = resp.json()['group_id']
                elif resp.status_code == 404:
                    raise KeyError(
                        "API returned 404 on import_type_ship_info id: {}\nCheck to make sure this entry still exists or if the database is corrupted.".format(
                            item["type_id"]))
                else:
                    raise ConnectionError(
                        "api import_type_ship_info info call got: {} from api".format(resp.status_code))
            except requests.exceptions.Timeout:
                print("API Timeout occurred, will retry")
                time.sleep(5)
                importFromAPI(item)

        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT type_id FROM ships WHERE type_name IS NULL")
            to_update = cursor.fetchall()
            print("Downloading ship info for {} types from CCP API, this can take a few minutes".format(len(to_update)))
            pool = ThreadPool(int(self.config_file['api_import']['threads']))
            pool.map(importFromAPI, to_update)
            pool.close()
            pool.join()
            for i in to_update:
                cursor.execute("REPLACE INTO item_types(%s) VALUES (%s)" % (
                    ",".join(i.keys()), ",".join(str(x) for x in i.values())))
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
