from sqlalchemy.orm import scoped_session, Session
from . import channel_manager as cm
from . import zk as zk
from . import static_data_import as static_data
from . import EVEsso
from . import RouteMapper
from . import InsightAdmins
import database
import InsightUtilities
import discord
from distutils.version import LooseVersion
import requests
import aiohttp
import platform
import traceback
import sys


class service_module(object):
    def __init__(self):
        self.cli_args = InsightUtilities.InsightArgumentParser.get_cli_args()
        self.welcome()
        self.config = InsightUtilities.ConfigLoader()
        self._header_dict = {}
        self.update_available()
        self._import_everything_flag = False
        self._import_check()
        self._db_manager = database.setup_database(self)
        self._sc_session: scoped_session = self._db_manager.get_scoped_session()
        InsightUtilities.DBSessions(sc_session=self._sc_session)
        self.static_data_import = static_data.static_data_import(self, self._import_everything_flag)
        self.routes = RouteMapper.RouteMapper(self)
        self.routes.setup_load()
        self.sso = EVEsso.EVEsso(self)
        self.channel_manager = cm.Channel_manager(self)
        self.zk_obj = zk.zk(self)
        self._admin_module = InsightAdmins.InsightAdmins()
        self.motd = self._read_motd()

    def get_headers(self, lib_requests=False) ->dict:
        key = 'requests' if lib_requests else 'aiohttp'
        if self._header_dict.get(key) is None:
            try:
                tmp_dict = {}
                from_field = self.config.get("HEADERS_FROM_EMAIL")
                if from_field:
                    tmp_dict['From'] = from_field
                else:
                    print("You are missing the 'from' email field in your config file. It is recommended to set this to "
                          "your webmaster email to include in HTTP request headers from Insight.")
                tmp_dict['Maintainer'] = 'admin@eveinsight.net (https://git.eveinsight.net)'
                web_lib = 'requests/{}'.format(requests.__version__) if lib_requests else 'aiohttp/{}'.format(aiohttp.__version__)
                tmp_dict['User-Agent'] = 'Insight/{} ({}; {}) Python/{}'.format(str(self.get_version()), platform.platform(aliased=True, terse=True), web_lib, platform.python_version())
                self._header_dict[key] = tmp_dict
            except Exception as ex:
                print('{} error when loading request headers.'.format(ex))
                traceback.print_exc()
                sys.exit(1)
        return self._header_dict[key]

    def _read_motd(self):
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

    def _import_check(self):
        try:
            with open(self.config.get("SQLITE_DB_PATH"),'r'):
                if not self.cli_args.skip_api_import:
                    self._import_everything_flag = True
        except FileNotFoundError:
            print("{} does not exist. Forcing first time static data import.".format(self.config.get("SQLITE_DB_PATH")))
            self._import_everything_flag = True

    def get_session(self)-> Session:
        """

        :rtype: Session
        """
        session_object: Session = self._sc_session()
        assert isinstance(session_object,Session)
        return session_object

    def close_session(self):
        self._sc_session.remove()

    def welcome(self):
        """Prints a welcome message with current version."""
        div = '==============================================================================================='
        print(div)
        print('Insight {} (Database {}) (discord.py v{}) on {} with Python/{}'.format(str(self.get_version()),
                                                                                      str(self.get_db_version()),
                                                                                      str(discord.__version__),
                                                                                      platform.platform(aliased=True, terse=True),
                                                                                      platform.python_version()))
        print("Insight is released under the GNU General Public License v3.0. See the included 'License.md' file.")
        print("Additional support is available at https://wiki.eveinsight.net")
        print(div)

    def update_available(self):
        giturl = 'https://api.github.com/repos/Nathan-LS/Insight/releases/latest'
        try:
            resp = requests.get(url=giturl, headers=self.get_headers(lib_requests=True), timeout=5, verify=True)
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
        return self._admin_module.is_admin(user_id)

    def shutdown(self):
        print('Attempting to shut down the database connections...')
        self._db_manager.shutdown()

    @classmethod
    def get_version(cls):
        version_str = 'v1.6.0'
        return LooseVersion(version_str)

    @classmethod
    def get_db_version(cls):
        version_str = 'v2.4.0'
        return LooseVersion(version_str)
