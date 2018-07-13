from sqlalchemy.orm import scoped_session, Session
from . import channel_manager as cm
from . import zk as zk
from . import static_data_import as static_data
from . import EVEsso
import database
import argparse
import configparser
import sys


class service_module(object):
    def __init__(self):
        self.config_file = configparser.ConfigParser()
        self.cli_args = self.__read_cli_args()
        self.config_file.read(self.__read_config_file())
        self.__import_everything_flag = False
        self.__import_check()
        self.__sc_session: scoped_session = database.setup_database(self).get_scoped_session()
        self.static_data_import = static_data.static_data_import(self,self.__import_everything_flag)
        self.sso = EVEsso.EVEsso(self)
        self.channel_manager = cm.Channel_manager(self)
        self.zk_obj = zk.zk(self)

    def __read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--config", "-c",
                            help="Specifies a config file other than the default 'config.ini' to run the program with",
                            default="config.ini")
        parser.add_argument("--debug_km","-km",
                            help="Start the application in debug mode to send kms starting at and above this id through all channel feeds.",
                            type=int)
        parser.add_argument("--force_ctime","-fc",
                            action="store_true",
                            help="If --debug_km is set, this flag will push kms to feeds with their time occurrence set to now.",
                            default=False)
        parser.add_argument("--debug_limit","-limit",
                            help="Sets the total limit of debug kms to push through feeds before exiting the program. Default is unlimited.",
                            type=int)
        parser.add_argument("--api_import","-api",action="store_true",
                            help="Sets the bot to import all data from the SDE database and EVE ESI.",default=False)
        parser.add_argument("--sde_db","-sde",
                            help="Specifies the name of the SDE database file relative to main.py. Download and extract the "
                                 "sqlite-latest.sqlite file from https://www.fuzzwork.co.uk/dump/",
                            type=str, default="sqlite-latest.sqlite")
        return parser.parse_args()

    def __read_config_file(self):
        try:
            with open(self.cli_args.config, 'r'):
                return self.cli_args.config
        except FileNotFoundError:
            print("The config file '{0}' could not be found. Try renaming the file 'default-config.ini' to '{0}'".format(str(self.cli_args.config)))
            sys.exit(1)

    def __import_check(self):
        try:
            with open(self.config_file['sqlite_database']['filename'],'r'):
                if self.cli_args.api_import:
                    self.__import_everything_flag = True
        except FileNotFoundError:
            print("{} does not exist. Forcing first time static data import.".format(self.config_file['sqlite_database']['filename']))
            self.__import_everything_flag = True

    def get_session(self)-> Session:
        """

        :rtype: Session
        """
        session_object: Session = self.__sc_session()
        assert isinstance(session_object,Session)
        return session_object

    def close_session(self):
        self.__sc_session.remove()