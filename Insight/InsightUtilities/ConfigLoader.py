from .InsightSingleton import InsightSingleton
from .InsightArgumentParser import InsightArgumentParser
import os
import sys
import configparser
import traceback


class ConfigLoader(metaclass=InsightSingleton):
    def __init__(self, exit_no_config_file=False):
        cli_args = InsightArgumentParser.get_cli_args()
        self._config_file_path = cli_args.config
        self.config_file_exists = False
        if self._config_file_path:
            if exit_no_config_file and not os.path.exists(self._config_file_path):
                sys.stderr.write("A config file was specified but the file was not found and is required. Please create the file '{}'".format(self._config_file_path))
                sys.exit(1)
            if os.path.exists(self._config_file_path):
                self.config_file_exists = True
        self.config_file = configparser.ConfigParser()
        self.config_file.read(self._config_file_path)
        self.config_mapping = {}
        self._load_all_options()

    def config_file_reparse(self):
        self.config_file = configparser.ConfigParser()
        self.config_file.read(self._config_file_path)

    def parse_config_val(self, ref_key, cfile_section, cfile_option, env_key, fail_if_empty=False, fallback_val="",
                         nonotify=False):
        config_key = ref_key.upper()
        config_val = os.getenv(env_key, None)
        if config_val is not None:
            pass
        else:
            try:
                if self.config_file_exists:
                    config_val = self.config_file.get(section=cfile_section, option=cfile_option, fallback=None)
            except (configparser.NoSectionError, configparser.NoOptionError):
                config_val = None
        if not config_val:
            if fail_if_empty:
                sys.stderr.write("Error: The config value: '{}' must be set in either an environmental variable "
                                 "or the config file.\nENV var to set: '{}'\n"
                                 "Config file section and option to set: '{}' -> '{}'\n\n"
                                 "".format(ref_key, env_key, cfile_section, cfile_option))
                sys.exit(1)
            else:
                if not nonotify:
                    sys.stderr.write("No config value was set for '{}' through either environmental variables or the config file. "
                          "Using the default value of: '{}'\n".format(ref_key, fallback_val))
                config_val = fallback_val
        self.config_mapping[config_key] = config_val
        return

    def get(self, ref_key: str):
        val = self.config_mapping.get(ref_key)
        if val is None:
            traceback.print_stack()
            sys.stderr.write("Calling for invalid config key: '{}'".format(ref_key))
            sys.exit(1)
        return val

    def _load_all_options(self):
        self.parse_config_val("SQLITE_DB_PATH", "sqlite_database", "filename", "SQLITE_DB_PATH", True)
        self.parse_config_val("HEADERS_FROM_EMAIL", "headers", "from", "HEADERS_FROM_EMAIL", False, "")
        self.parse_config_val("DISCORD_TOKEN", "discord", "token", "DISCORD_TOKEN", True)
        self.parse_config_val("CCP_CLIENT_ID", "ccp_developer", "client_id", "CCP_CLIENT_ID", True)
        self.parse_config_val("CCP_SECRET_KEY", "ccp_developer", "secret_key", "CCP_SECRET_KEY", True)
        self.parse_config_val("CCP_CALLBACK_URL", "ccp_developer", "callback_url", "CCP_CALLBACK_URL", False, "https://github.eveinsight.net/Insight/callback")
        self.parse_config_val("DISCORDBOTS_APIKEY", "discordbots.org", "discordbots_apikey", "DISCORDBOTS_APIKEY",
                              False, "", True)
