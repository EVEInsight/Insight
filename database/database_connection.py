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

    def test_connection(self):
        print("Testing database connection")
        try:
            test_con = mysql.connector.connect(**self.db_config)
        except Exception as ex:
            print(ex)
            if test_con:
                test_con.rollback()
            return False
        finally:
            if test_con:
                test_con.close()
                print("Connection successful!")
                return True

    def config(self):
        return self.db_config