from service.service import service_module
from sqlalchemy.orm import Session, scoped_session
import platform
import requests
import aiohttp
from tests.mocks import ChannelManager


class ServiceModule(service_module):
    def __init__(self, db_session):
        self.session = db_session
        self.cli_args = self._read_cli_args()
        self.channel_manager = ChannelManager.ChannelManager(self)

    def get_session(self):
        if isinstance(self.session, scoped_session):
            ses= self.session()
            return ses
        else:
            return self.session

    def close_session(self):
        if isinstance(self.session, scoped_session):
            self.session.remove()
        else:
            self.session.close()

    def get_headers(self, lib_requests=False) ->dict:
        tmp_dict = {}
        tmp_dict['Maintainer'] = 'nathan@nathan-s.com (https://github.com/Nathan-LS/Insight)'
        web_lib = 'requests/{}'.format(requests.__version__) if lib_requests else 'aiohttp/{}'.format(aiohttp.__version__)
        tmp_dict['User-Agent'] = 'Insight Test Suite/{} ({}; {}) Python/{}'.format(str(self.get_version()), platform.platform(aliased=True, terse=True), web_lib, platform.python_version())
        return tmp_dict
