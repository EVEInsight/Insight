from . import service
from urllib.parse import quote
import urllib.parse as urlparse
import requests
from requests.auth import HTTPBasicAuth
import json


class EVEsso(object):
    def __init__(self, service_module):
        assert isinstance(service_module, service.service_module)
        self.service = service_module
        self.__client_id = None
        self.__client_secret = None
        self.__callback = ""
        self._token_url = "https://login.eveonline.com/oauth/token"
        self._verify_url = "https://login.eveonline.com/oauth/verify"
        self._login_url = ""
        self.__get_config()

    def __get_config(self):
        """gets the configuration from the config file, exits if invalid or no keys"""
        self.__client_id = self.service.config_file["ccp_developer"]["client_id"]
        self.__client_secret = self.service.config_file["ccp_developer"]["secret_key"]
        self.__callback = self.service.config_file["ccp_developer"]["callback_url"]
        if not self.__client_id or not self.__client_secret or not self.__callback:
            print("You are missing a CCP developer application key and secret. Please set these in the config file.")
            exit(1)
        self._login_url = "https://login.eveonline.com/oauth/authorize?response_type=code&redirect_uri={cb}&client_id={cid}&scope={scopes}".format(
            cb=self.__callback, cid=self.__client_id, scopes=self.__get_scopes())

    def __get_scopes(self):
        _scopes = quote(
            "esi-characters.read_contacts.v1 esi-corporations.read_contacts.v1 esi-alliances.read_contacts.v1")
        return str(_scopes)

    def get_sso_login(self):
        return self._login_url

    def get_callback_example(self):
        return "{}{}".format(self.__callback, "?code=ExampleCallbackAuthCode")

    def clean_auth_code(self, auth_str):
        parsed_str = urlparse.urlparse(auth_str)
        code = (urlparse.parse_qs(parsed_str.query)['code'])
        return code[0]

    def get_token_from_auth(self, auth_code):
        auth_header = (HTTPBasicAuth(self.__client_id, self.__client_secret))
        headers = {"Content-Type": "application/json", "User-Agent": "InsightDiscordKillfeeds"}
        payload = {"grant_type": "authorization_code", "code": auth_code}
        response = requests.post(url=self._token_url, auth=auth_header, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Non 200 when getting token from auth.")

    def get_token(self, token_row):
        """sets the token or deletes the row if it has been revoked"""
        assert isinstance(token_row, tb_tokens)
        db: Session = self.service.get_session()
        auth_header = (
            HTTPBasicAuth(self.__client_id, self.__client_secret))
        headers = {"Content-Type": "application/json", "User-Agent": "InsightDiscordKillfeeds"}
        payload = {"grant_type": "refresh_token", "refresh_token": token_row.refresh_token}
        try:
            response = requests.post(url=self._token_url, auth=auth_header, data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                token_row.token = response.json().get("access_token")
            elif response.status_code == 400:
                db.delete(token_row)
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_char(self, token):
        headers = {"Authorization": "Bearer {}".format(token), "Content-Type": "application/json",
                   "User-Agent": "InsightDiscordKillfeeds"}
        try:
            response = requests.get(url=self._verify_url, headers=headers)
            if response.status_code == 200:
                return (response.json()).get("CharacterID")
            else:
                return None
        except Exception as ex:
            print(ex)
            return None


from database.db_tables import tb_tokens
from .service import *
