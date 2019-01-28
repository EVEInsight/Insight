from . import service
from urllib.parse import quote
import urllib.parse as urlparse
import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import InsightExc
import InsightLogger


class EVEsso(object):
    def __init__(self, service_module):
        assert isinstance(service_module, service.service_module)
        self.logger = InsightLogger.InsightLogger.get_logger('SSO', 'SSO.log')
        self.service = service_module
        self._client_id = None
        self._client_secret = None
        self._callback = ""
        self._token_url = "https://login.eveonline.com/oauth/token"
        self._verify_url = "https://login.eveonline.com/oauth/verify"
        self._revoke_url = "https://login.eveonline.com/oauth/revoke"
        self._login_url = ""
        self._get_config()
        if self.service.cli_args.auth:
            self._console_auth_mode()

    def _console_auth_mode(self):
        print("==================Insight auth code converter mode==================")
        print("Using SSO config parameters from file: {}".format(self.service.cli_args.config))
        print("Client ID: ****{}".format(self._client_id[-4:]))
        print("Client Secret: ****{}".format(self._client_secret[-4:]))
        print("Navigate to this URL:\n\n{}\n\nSign in, and paste the callback URL into this console prompt:"
              "".format(self.get_sso_login()))
        with open(0) as i:
            sys.stdin = i
            auth_input = input().strip()
        print("\nRefresh token: {}".format(self.get_token_from_auth(self.clean_auth_code(auth_input)).get("refresh_token")))
        sys.exit(0)

    def _get_config(self):
        """gets the configuration from the config file, exits if invalid or no keys"""
        self._client_id = self.service.config_file["ccp_developer"]["client_id"]
        self._client_secret = self.service.config_file["ccp_developer"]["secret_key"]
        self._callback = self.service.config_file["ccp_developer"]["callback_url"]
        if not self._client_id or not self._client_secret or not self._callback:
            print("You are missing a CCP developer application key and secret. Please set these in the config file.")
            sys.exit(1)
        self._login_url = "https://login.eveonline.com/oauth/authorize?response_type=code&redirect_uri={cb}&client_id={cid}&scope={scopes}".format(
            cb=self._callback, cid=self._client_id, scopes=self._get_scopes())

    def _get_scopes(self):
        _scopes = quote(
            "esi-characters.read_contacts.v1 esi-corporations.read_contacts.v1 esi-alliances.read_contacts.v1")
        return str(_scopes)

    def get_sso_login(self):
        return self._login_url

    def get_callback_example(self):
        return "{}{}".format(self._callback, "?code=ExampleCallbackAuthCode")

    def clean_auth_code(self, auth_str):
        parsed_str = urlparse.urlparse(auth_str)
        code = (urlparse.parse_qs(parsed_str.query)['code'])
        return code[0]

    def get_token_from_auth(self, auth_code):
        auth_header = (HTTPBasicAuth(self._client_id, self._client_secret))
        headers = {"Content-Type": "application/json", **self.service.get_headers(lib_requests=True)}
        payload = {"grant_type": "authorization_code", "code": auth_code}
        response = requests.post(url=self._token_url, auth=auth_header, data=json.dumps(payload), headers=headers,
                                 timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Non 200 when getting token from auth.")

    def get_token(self, token_row):
        """sets the token or deletes the row if it has been revoked"""
        assert isinstance(token_row, tb_tokens)
        db: Session = self.service.get_session()
        auth_header = (
            HTTPBasicAuth(self._client_id, self._client_secret))
        headers = {"Content-Type": "application/json", **self.service.get_headers(lib_requests=True)}
        payload = {"grant_type": "refresh_token", "refresh_token": token_row.refresh_token}
        try:
            if token_row.error_count >= 4:
                db.delete(token_row)
                self.logger.info('Token {} has been deleted after {} errors.'.format(token_row.token_id, token_row.error_count))
                return
            response = requests.post(url=self._token_url, auth=auth_header, data=json.dumps(payload), headers=headers,
                                     timeout=60)
            if response.status_code == 200:
                token_row.token = response.json().get("access_token")
                token_row.error_count = 0
                self.logger.info('Response 200 on token ID: {} when getting token.'.format(token_row.token_id))
            elif response.status_code == 420:
                self.logger.warning('Response 420 on token ID: {} when getting token. Headers: {} Body: {}'.
                                    format(token_row.token_id, response.headers, response.json()))
                token_row.token = None
            elif 400 <= response.status_code < 500:
                self.logger.warning('Response {} on token ID: {} when getting token. Headers: {} Body: {}'.
                                    format(response.status_code, token_row.token_id, response.headers, response.json()))
                token_row.token = None
                token_row.error_count += 1
            else:
                token_row.token = None
                self.logger.warning('Response {} on token ID: {} when getting token. Headers: {} Body: {}'.
                                    format(response.status_code, token_row.token_id, response.headers, response.json()))
        except Exception as ex:
            token_row.token = None
            print(ex)
            self.logger.exception(ex)

    def delete_token(self, row):
        assert isinstance(row, tb_tokens)
        db: Session = self.service.get_session()
        ref_token = row.refresh_token
        try:
            db.delete(row)
            db.commit()
        except Exception as ex:
            print(ex)
            raise InsightExc.Db.DatabaseError("Database Error: Unable to delete token from the database")
        finally:
            db.close()
            try:
                auth_header = (
                    HTTPBasicAuth(self._client_id, self._client_secret))
                headers = {"Content-Type": "application/json", **self.service.get_headers(lib_requests=True)}
                payload = {"token_type_hint": "refresh_token", "token": ref_token}
                response = requests.post(url=self._revoke_url, auth=auth_header, data=json.dumps(payload),
                                         headers=headers, timeout=60, verify=True)
                if response.status_code != 200:
                    raise InsightExc.SSO.SSOerror
            except:
                raise InsightExc.SSO.SSOerror('The token was not revoked from EVE SSO. Please visit '
                                              'https://community.eveonline.com/support/third-party-applications/ '
                                              'to ensure your token is properly deleted.')

    def get_char(self, token):
        headers = {"Authorization": "Bearer {}".format(token), "Content-Type": "application/json",
                   **self.service.get_headers(lib_requests=True)}
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
