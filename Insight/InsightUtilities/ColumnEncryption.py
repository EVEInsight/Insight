from .InsightSingleton import InsightSingleton
from .InsightArgumentParser import InsightArgumentParser
import secrets
import configparser
import sys
import os


class ColumnEncryption(metaclass=InsightSingleton):
    def __init__(self):
        self._key = None
        cli_args = InsightArgumentParser.get_cli_args()
        self._config_file_path = cli_args.config

    def _generate_new_key(self) -> str:
        return str(secrets.token_urlsafe(64))

    def _set_key(self, new_key):
        self._key = new_key

    def _set_random_key(self):
        self._key = self._generate_new_key()

    def print_file_warning(self, tmp_key):
        print("WARNING: Generated a key in memory. \nThis key will encrypt token table columns but the encryption "
              "key will be wiped from memory after the bot is stopped. This key will not be displayed again."
              "\nPlease set the \"INSIGHT_ENCRYPTION_KEY\" "
              "environmental variable to the following generated key.\n\nEncryption key: \"{}\"\n".format(tmp_key))

    def _load_key(self):
        config_val = os.getenv("INSIGHT_ENCRYPTION_KEY", "")
        if len(config_val) == 0:
            pass
        else:
            self._set_key(config_val)
            return
        try:
            with open(self._config_file_path, 'r'):
                pass
            cfile = configparser.ConfigParser()
            cfile.read(self._config_file_path)
            if not cfile.get("encryption", "secret_key"):
                tmp_key = self._generate_new_key()
                self._set_key(tmp_key)
                self.print_file_warning(tmp_key)
            else:
                self._set_key(cfile.get("encryption", "secret_key"))
                print("Token table encryption key was loaded from the config file. \nNOTE: you can now pass the "
                      "encryption key through the \"INSIGHT_ENCRYPTION_KEY\" environmental variable removing the need "
                      "to persist the config file on a Docker volume.")
        except FileNotFoundError:
            tmp_key = self._generate_new_key()
            self.print_file_warning(tmp_key)
            self._set_key(tmp_key)

    def get_key(self):
        if not isinstance(self._key, str):
            self._load_key()
        return self._key

    def reset_key(self):
        """overwrite the currently configured key in the config file and install a new token"""
        try:
            with open(self._config_file_path, 'r'):
                pass
            cfile = configparser.ConfigParser()
            cfile.read(self._config_file_path)
            cfile.set("encryption", "secret_key", "")
            with open(self._config_file_path, 'w') as cf:
                cfile.write(cf)
        except FileNotFoundError:
            pass
        self._set_key(None)
        self.get_key()

    @classmethod
    def helper_get_key(cls):
        return cls().get_key()
