from service.service import service_module
import platform
import requests
import aiohttp


class ServiceModule(service_module):
    def __init__(self, db_session):
        self.session = db_session

    def get_session(self):
        return self.session

    def get_headers(self, lib_requests=False) ->dict:
        tmp_dict = {}
        tmp_dict['Maintainer'] = 'nathan@nathan-s.com (https://github.com/Nathan-LS/Insight)'
        web_lib = 'requests/{}'.format(requests.__version__) if lib_requests else 'aiohttp/{}'.format(aiohttp.__version__)
        tmp_dict['User-Agent'] = 'Insight Test Suite/{} ({}; {}) Python/{}'.format(str(self.get_version()), platform.platform(aliased=True, terse=True), web_lib, platform.python_version())
        return tmp_dict
