from service.service import service_module
from sqlalchemy.orm import Session, scoped_session
import platform
import requests
import aiohttp
from tests.mocks import ChannelManager
import os
import InsightUtilities


class ServiceModule(service_module):
    def __init__(self, db_session):
        self.session = db_session
        self.cli_args = InsightUtilities.InsightArgumentParser.get_cli_args()
        self.channel_manager = ChannelManager.ChannelManager(self)

    def get_session(self):
        if isinstance(self.session, scoped_session):
            ses = self.session()
            return ses
        elif isinstance(self.session, Session):
            return self.session
        else:
            raise NotImplementedError

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

    @property
    def config_file(self):
        return {"ccp_developer":
                {"client_id": os.environ.get("sso_client_id"),
                 "secret_key": os.environ.get("sso_secret_key"),
                 "callback_url": os.environ.get("sso_callback_url")}
                }
