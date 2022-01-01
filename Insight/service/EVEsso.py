from . import service
from urllib.parse import quote
import urllib.parse as urlparse
import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import InsightExc
import InsightLogger
import asyncio
import secrets
import base64
from jose import jwt
from jose.exceptions import JWTClaimsError
import time


class EVEsso(object):
    def __init__(self, service_module):
        assert isinstance(service_module, service.service_module)
        self.logger = InsightLogger.InsightLogger.get_logger('SSO', 'SSO.log')
        self.service = service_module
        self._client_id = None
        self._client_secret = None
        self._callback = ""
        self._authorize_url = "https://login.eveonline.com/v2/oauth/authorize"
        self._token_url = "https://login.eveonline.com/v2/oauth/token"
        self._revoke_url = "https://login.eveonline.com/v2/oauth/revoke"
        self._jwk_set_url = "https://login.eveonline.com/oauth/jwks"
        self._get_config()
        self.callback_states = {} #callback states waiting; key = unique state param, value = async event
        self.callback_codes = {} #callback states waiting; key = unique state param, value = code
        self.callback_states_lock = asyncio.Lock(loop=asyncio.get_event_loop())
        self.jwk_set = {}
        self._load_jwt_key_sets()
        if self.service.cli_args.auth:
            self._console_auth_mode()

    def _console_auth_mode(self):
        print("==================Insight auth code converter mode==================")
        print("Using SSO config parameters from file: {}".format(self.service.cli_args.config))
        print("Client ID: ****{}".format(self._client_id[-4:]))
        print("Client Secret: ****{}".format(self._client_secret[-4:]))
        print("Navigate to this URL:\n\n{}\n\nSign in, and paste the callback URL into this console prompt:"
              "".format(self.get_sso_login(secrets.token_urlsafe(12))))
        with open(0) as i:
            sys.stdin = i
            auth_input = input().strip()
        print("\nRefresh token: {}".format(self.get_token_from_auth(self.clean_auth_code(auth_input)).get("refresh_token")))
        sys.exit(0)

    def _get_config(self):
        """gets the configuration from the config file, exits if invalid or no keys"""
        self._client_id = self.service.config.get("CCP_CLIENT_ID")
        self._client_secret = self.service.config.get("CCP_SECRET_KEY")
        self._callback = self.service.config.get("CCP_CALLBACK_URL")
        if not self._client_id or not self._client_secret or not self._callback:
            print("You are missing a CCP developer application key and secret. Please set these in the config file.")
            sys.exit(1)

    def _load_jwt_key_sets(self):
        error_count = 0
        while 10 >= error_count:
            error_count += 1
            try:
                r = requests.get(url=self._jwk_set_url, timeout=5, verify=True)
                r.raise_for_status()
                if r.status_code == 200:
                    d = r.json()
                    jwk_sets = d["keys"]
                    self.jwk_set = next((item for item in jwk_sets if item["alg"] == "RS256"))
                    break
                else:
                    print("Got response code when attempting to load jwt key sets... {}".format(r.status_code))
            except Exception as ex:
                print("Error when attempting to load jwt key sets.\n{}".format(ex))
                time.sleep(3)

    def _get_scopes(self):
        _scopes = quote(
            "esi-characters.read_contacts.v1 esi-corporations.read_contacts.v1 esi-alliances.read_contacts.v1")
        return str(_scopes)

    async def generate_sso_state(self):
        """returns a randomized unique state code that later retrieves an asyncio event object"""
        loop_count = 0
        while True:
            async with self.callback_states_lock:
                s = secrets.token_urlsafe(12)
                if self.callback_states.get(s) is None:
                    self.callback_states[s] = asyncio.Event()
                    return s
                else:
                    loop_count += 1
                    if loop_count > 5:
                        raise InsightExc.baseException.InsightException(message="Could not generate a unique state")

    async def validate_state(self, state_str):
        """return true if state is str has a valid event listener specified"""
        async with self.callback_states_lock:
            return state_str in self.callback_states

    async def invalidate_state(self, state_str):
        """invalidate a state"""
        async with self.callback_states_lock:
            if state_str in self.callback_states:
                self.callback_states.pop(state_str)
            if state_str in self.callback_codes:
                self.callback_codes.pop(state_str)

    async def get_state_event(self, state_str):
        async with self.callback_states_lock:
            e = self.callback_states.get(state_str, None)
            if not e:
                raise KeyError
            else:
                return e

    async def get_state_code(self, state_str):
        async with self.callback_states_lock:
            e = self.callback_codes.get(state_str, None)
            if not e:
                raise KeyError
            else:
                return e

    async def set_state_code(self, state_str, state_code):
        async with self.callback_states_lock:
            self.callback_codes[state_str] = state_code
            e: asyncio.Event = self.callback_states.get(state_str, None)
            if isinstance(e, asyncio.Event):
                e.set()

    def get_sso_login(self, state):
        s = "{auth_url}?response_type=code&redirect_uri={cb}&client_id={cid}&scope={scopes}&state={state}".format(auth_url=self._authorize_url,
            cb=self._callback, cid=self._client_id, scopes=self._get_scopes(), state=state)
        return s

    def get_callback_example(self):
        return "{}{}".format(self._callback, "?code=ExampleCallbackAuthCode")

    def clean_auth_code(self, auth_str):
        parsed_str = urlparse.urlparse(auth_str)
        code = (urlparse.parse_qs(parsed_str.query)['code'])
        return code[0]

    def get_token_from_auth(self, auth_code):
        headers = {"Content-Type": "application/x-www-form-urlencoded", **self.service.get_headers(lib_requests=True),
                   "Authorization": "Basic {}".format((base64.urlsafe_b64encode("{}:{}".format(self._client_id, self._client_secret).encode())).decode("utf-8")),
                   "Host": "login.eveonline.com"}
        payload = {"grant_type": "authorization_code", "code": auth_code}
        response = requests.post(url=self._token_url, data=payload, headers=headers, timeout=60, verify=True)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Non 200 when getting token from auth.")

    def get_token(self, token_row):
        """gets a refresh token"""
        assert isinstance(token_row, tb_tokens)
        db: Session = self.service.get_session()
        headers = {"Content-Type": "application/x-www-form-urlencoded", **self.service.get_headers(lib_requests=True),
                   "Authorization": "Basic {}".format((base64.urlsafe_b64encode("{}:{}".format(self._client_id, self._client_secret).encode())).decode("utf-8")),
                   "Host": "login.eveonline.com"}
        payload = {"grant_type": "refresh_token", "refresh_token": token_row.refresh_token}
        try:
            if token_row.error_count >= 4:
                db.delete(token_row)
                self.logger.info('Token {} has been deleted after {} errors.'.format(token_row.token_id, token_row.error_count))
                return
            response = requests.post(url=self._token_url, data=payload, headers=headers, timeout=60, verify=True) # https://docs.esi.evetech.net/docs/sso/refreshing_access_tokens.html
            if response.status_code == 200:
                rjson = response.json()
                if token_row.refresh_token != rjson.get("refresh_token"):
                    token_row.refresh_token = rjson.get("refresh_token") # with v2 it's possible for this to change
                token_row.token = rjson.get("access_token")
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
                headers = {"Content-Type": "application/x-www-form-urlencoded", **self.service.get_headers(lib_requests=True)}
                payload = {"token_type_hint": "refresh_token", "token": ref_token}
                response = requests.post(url=self._revoke_url, auth=auth_header, data=payload,
                                         headers=headers, timeout=60, verify=True)
                if response.status_code != 200:
                    raise InsightExc.SSO.SSOerror
            except:
                raise InsightExc.SSO.SSOerror('The token was not revoked from EVE SSO. Please visit '
                                              'https://community.eveonline.com/support/third-party-applications/ '
                                              'to ensure your token is properly deleted.')

    def get_char(self, token):
        """returns the character ID from the JWT token"""
        s = self.verify_jwt(token).get("sub")
        char_id = int(s.replace("CHARACTER:EVE:", ""))
        return char_id

    def verify_jwt(self, token):
        """returns the decoded token or raises an exception if there is a problem"""
        try:
            return jwt.decode(token, self.jwk_set, algorithms=self.jwk_set["alg"], issuer="login.eveonline.com")
        except JWTClaimsError:
            try:
                return jwt.decode(token, self.jwk_set, algorithms=self.jwk_set["alg"], issuer="https://login.eveonline.com")
            except JWTClaimsError:
                raise InsightExc.SSO.SSOerror("JWT verify failed as the issuer host / domain does not match the expected value.")
        except Exception as ex:
            self.logger.exception(ex)
            raise InsightExc.SSO.SSOerror("JWT verify failed.")



from database.db_tables import tb_tokens
from .service import *
