import time

import mysql.connector


class db_con(object):
    """Config and testing for a MySQL connection"""

    def __init__(self, cf_file, args):
        self.config_file = cf_file
        self.arguments = args
        self.db_config = {'host': self.config_file["database"]["host"],
                          'port': self.config_file["database"]["port"],
                          'database': self.config_file["database"]["db"],
                          'user': self.config_file["database"]["user"],
                          'password': self.config_file["database"]["pass"]
                          }
        self.retry_test_connect()

    def test_connection(self):
        print("Testing database connection")
        try:
            test_con = mysql.connector.connect(**self.db_config)
            if test_con:
                test_con.close()
                print("Connection successful!")
                return True
        except Exception as ex:
            print(ex)
            return False

    def retry_test_connect(self):
        retryCount = int(self.config_file['database']['initial_max_retry'])
        while retryCount >= 0:
            if not self.test_connection():
                print("Unable to connect to the database, trying again after retry delay. {} attempts remain".format(
                    str(retryCount)))
                time.sleep(int(self.config_file['database']['initial_retry_delay']))
            else:
                return
            retryCount -= 1
        exit(1)  # exit if max connection retry exceeded

    def config(self):
        return self.db_config