from sqlalchemy.orm import scoped_session, Session
from . import channel_manager as cm
from . import zk as zk
from . import static_data_import as static_data
from . import EVEsso
from . import RouteMapper
from . import InsightAdmins
import database
import argparse
import configparser
import sys
import discord
from distutils.version import LooseVersion
import requests
import secrets
import aiohttp
import platform
import traceback
import sys

__passkey = None


class service_module(object):
    def __init__(self, multiproc_dict):
        self.__multiproc_dict:dict = multiproc_dict
        self.cli_args = self.__read_cli_args()
        self.set_crash_recovery(self.cli_args.crash_recovery, None)
        self.config_file = configparser.ConfigParser()
        self.config_file.read(self.read_config_file(self.cli_args.config))
        self.__header_dict = {}
        self.welcome()
        self.__import_everything_flag = False
        self.__import_check()
        self.__db_manager = database.setup_database(self)
        self.__sc_session: scoped_session = self.__db_manager.get_scoped_session()
        self.static_data_import = static_data.static_data_import(self,self.__import_everything_flag)
        self.routes = RouteMapper.RouteMapper(self)
        self.sso = EVEsso.EVEsso(self)
        self.channel_manager = cm.Channel_manager(self)
        self.zk_obj = zk.zk(self)
        self.__admin_module = InsightAdmins.InsightAdmins()
        self.motd = self.__read_motd()
        self.set_crash_recovery(self.cli_args.crash_recovery, self.__admin_module.get_default_admin())  # set id

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
        parser.add_argument("--skip_api_import", "-noapi", action="store_true",
                            help="Skip startup API static data import check.", default=False)
        parser.add_argument("--websocket", "-ws", action="store_true",
                            help="Enable the experimental secondary ZK websocket connection.", default=False)
        parser.add_argument("--defer_tasks", "-defer", action="store_true",
                            help="Defers slow tasks to run later instead of at startup.", default=False)
        parser.add_argument("--sde_db","-sde",
                            help="Specifies the name of the SDE database file relative to main.py. Download and extract the "
                                 "sqlite-latest.sqlite file from https://www.fuzzwork.co.uk/dump/",
                            type=str, default="sqlite-latest.sqlite")
        parser.add_argument("--crash_recovery", "-cr", action="store_true",
                            help="Automatically reboot Insight in the event of an application crash.", default=False)
        return parser.parse_args()

    def get_headers(self, lib_requests=False) ->dict:
        key = 'requests' if lib_requests else 'aiohttp'
        if self.__header_dict.get(key) is None:
            try:
                tmp_dict = {}
                from_field = self.config_file.get('headers', 'from', fallback='')
                if from_field:
                    tmp_dict['From'] = from_field
                else:
                    print("You are missing the 'from' email field in your config file. It is recommended to set this to "
                          "your webmaster email to include in HTTP request headers from Insight.")
                tmp_dict['Maintainer'] = 'nathan@nathan-s.com (https://github.com/Nathan-LS/Insight)'
                web_lib = 'requests/{}'.format(requests.__version__) if lib_requests else 'aiohttp/{}'.format(aiohttp.__version__)
                tmp_dict['User-Agent'] = 'Insight/{} ({}; {}) Python/{}'.format(str(self.get_version()), platform.platform(aliased=True, terse=True), web_lib, platform.python_version())
                self.__header_dict[key] = tmp_dict
            except Exception as ex:
                print('{} error when loading request headers.'.format(ex))
                traceback.print_exc()
                sys.exit(1)
        return self.__header_dict[key]

    @classmethod
    def read_config_file(cls, fname, newkey=False):
        try:
            with open(fname, 'r'):
                pass
            tmpConfig = configparser.ConfigParser()
            tmpConfig.read(fname)
            if not tmpConfig['encryption']['secret_key'] or newkey:
                print("Generating a new encryption secret key in config file.")
                tmpConfig['encryption']['secret_key'] = cls.generate_secret()
                with open(fname, 'w') as cf:
                    tmpConfig.write(cf)
            global __passkey
            __passkey = tmpConfig['encryption']['secret_key']
            return fname
        except FileNotFoundError:
            print("The config file '{0}' could not be found. Rename file 'default-config.ini' to '{0}'. "
                  "If you are using Insight with Docker make sure to check your volume directory, rename the "
                  "'default-config.ini' to 'config.ini', and populate the configuration values.".format(fname))
            sys.exit(1)

    def __read_motd(self):
        filename = 'motd.txt'
        print('Edit the message of the day file "{}" to send a message to all '
              'feeds on Insight startup. Edit the file to be blank to prevent Insight from sending '
              'a message of the day to all active feeds.'.format(filename))
        try:
            with open(filename, 'r') as f:
                text = f.read()
                if text.strip():
                    return text
                else:
                    return None
        except FileNotFoundError:
            with open(filename, 'w'):
                print('Creating empty motd file: "{}"'.format(filename))
                return None

    def __import_check(self):
        try:
            with open(self.config_file['sqlite_database']['filename'],'r'):
                if not self.cli_args.skip_api_import:
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

    def welcome(self):
        """Prints a welcome message with current version and displays alerts if new project updates are available."""
        div = '==============================================================================================='
        print(div)
        print('Insight {} (Database {}) (discord.py v{}) on {} with Python/{}'.format(str(self.get_version()),
                                                                                      str(self.get_db_version()),
                                                                                      str(discord.__version__),
                                                                                      platform.platform(aliased=True, terse=True),
                                                                                      platform.python_version()))
        self.update_available()
        print(div)

    def update_available(self):
        giturl = 'https://api.github.com/repos/Nathan-LS/Insight/releases/latest'
        try:
            resp = requests.get(url=giturl, headers=self.get_headers(lib_requests=True), timeout=25, verify=True)
            if resp.status_code == 200:
                data = resp.json()
                new_version = LooseVersion(data.get('tag_name'))
                if new_version > self.get_version():
                    print('A new version is available. Please visit {} to update.'.format(data.get('html_url')))
                    return True
                else:
                    return False
            else:
                return False
        except Exception as ex:
            print(ex)
            return False

    def is_admin(self, user_id):
        return self.__admin_module.is_admin(user_id)

    def shutdown(self):
        print('Attempting to shut down the database...')
        self.__db_manager.shutdown()

    def set_crash_recovery(self, mode_flag: bool, notify_user_id):
        if mode_flag is True and self.__multiproc_dict.get('crash_recovery') is not True:
            print('Insight crash recovery has been enabled. Insight will attempt to reboot up to 2 times in the '
                  'span of 30 minutes in the event of a crash.')
        self.__multiproc_dict['crash_recovery'] = mode_flag
        self.__multiproc_dict['notify_userid'] = notify_user_id

    @classmethod
    def get_version(cls):
        version_str = 'v1.3.1'
        return LooseVersion(version_str)

    @classmethod
    def get_db_version(cls):
        version_str = 'v2.4.0'
        return LooseVersion(version_str)

    @staticmethod
    def get_key():
        global __passkey
        return __passkey

    @staticmethod
    def generate_secret():
        return str(secrets.token_urlsafe(64))
