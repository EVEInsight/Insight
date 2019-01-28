from .InsightSingleton import InsightSingleton
from .InsightArgumentParser import InsightArgumentParser
import secrets
import configparser
import sys


class ColumnEncryption(metaclass=InsightSingleton):
    def __init__(self):
        self._key = None
        cli_args = InsightArgumentParser.get_cli_args()
        self._config_file_path = cli_args.config

    def _generate_new_key(self)->str:
        return str(secrets.token_urlsafe(64))

    def _set_key(self, new_key):
        self._key = new_key

    def _set_random_key(self):
        self._key = self._generate_new_key()

    def _load_key(self):
        try:
            with open(self._config_file_path, 'r'):
                pass
            cfile = configparser.ConfigParser()
            cfile.read(self._config_file_path)
            if not cfile.get("encryption", "secret_key"):
                print("Generating a new encryption secret key in config file.")
                cfile.set("encryption", "secret_key", self._generate_new_key())
                with open(self._config_file_path, 'w') as cf:
                    cfile.write(cf)
            self._set_key(cfile.get("encryption", "secret_key"))
        except FileNotFoundError:
            print("The config file '{0}' could not be found. Rename file 'default-config.ini' to '{0}'. "
                  "If you are using Insight with Docker make sure to check your volume directory, rename the "
                  "'default-config.ini' to 'config.ini', and populate the configuration values.".format(self._config_file_path))
            sys.exit(1)

    def get_key(self):
        if not isinstance(self._key, str):
            self._load_key()
        return self._key

    def reset_key(self):
        """overwrite the currently configured key in the config file and install a new token"""
        cfile = configparser.ConfigParser()
        cfile.read(self._config_file_path)
        cfile.set("encryption", "secret_key", "")
        with open(self._config_file_path, 'w') as cf:
            cfile.write(cf)
        self._set_key(None)
        self.get_key()

    @classmethod
    def helper_get_key(cls):
        return cls().get_key()
