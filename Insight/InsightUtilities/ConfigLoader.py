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

    def _parse_config_val(self, ref_key, cfile_section, cfile_option, fail_if_empty, fallback_val, nonotify):
        config_val = os.getenv(ref_key, "")
        if config_val:
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
                                 "".format(ref_key, ref_key, cfile_section, cfile_option))
                sys.exit(1)
            else:
                if not nonotify:
                    sys.stderr.write("No config value was set for '{}' through either environmental variables or the config file. "
                          "Using the default value of: '{}'\n".format(ref_key, fallback_val))
                config_val = fallback_val
        return config_val

    def parse_str(self, ref_key, cfile_section, cfile_option, fail_if_empty=False, fallback_val="",
                  nonotify=False):
        config_key = ref_key.upper()
        config_val = self._parse_config_val(ref_key, cfile_section, cfile_option, fail_if_empty,
                                            fallback_val, nonotify)
        self.config_mapping[config_key] = config_val

    def parse_list(self, ref_key, cfile_section, cfile_option, fail_if_empty=False, fallback_val="",
                  nonotify=False):
        config_key = ref_key.upper()
        config_val: str = self._parse_config_val(ref_key, cfile_section, cfile_option, fail_if_empty,
                                            fallback_val, nonotify)
        if len(config_val) > 0:
            parsed_items = (config_val.replace(":", ";")).split(";")
        else:
            parsed_items = []
        self.config_mapping[config_key] = parsed_items

    def parse_int(self, ref_key, cfile_section, cfile_option, fail_if_empty=False, fallback_val=0,
                  nonotify=False):
        config_key = ref_key.upper()
        config_val = self._parse_config_val(ref_key, cfile_section, cfile_option, fail_if_empty,
                                            fallback_val, nonotify)
        try:
            config_val = int(config_val)
        except ValueError:
            sys.stderr.write("Error with input for variable '{}'. Got '{}' but was expecting a valid integer.\n"
                             "".format(ref_key, config_val))
            sys.exit(1)
        self.config_mapping[config_key] = config_val

    def parse_bool(self, ref_key, cfile_section, cfile_option, fail_if_empty=False, fallback_val="FALSE",
                  nonotify=False):
        config_key = ref_key.upper()
        config_val = self._parse_config_val(ref_key, cfile_section, cfile_option, fail_if_empty,
                                            fallback_val, nonotify)
        try:
            if config_val.lower() in ["true", "t", "1"]:
                config_val = True
            elif config_val.lower() in ["false", "f", "0"]:
                config_val = False
            else:
                raise ValueError
        except ValueError:
            sys.stderr.write("Error with input for variable '{}'. Got '{}' but was expecting a valid boolean.\n"
                             "".format(ref_key, config_val))
            sys.exit(1)
        self.config_mapping[config_key] = config_val

    def get(self, ref_key: str):
        val = self.config_mapping.get(ref_key)
        if val is None:
            traceback.print_stack()
            sys.stderr.write("Calling for invalid config key: '{}'".format(ref_key))
            sys.exit(1)
        return val

    def _load_all_options(self):
        self.parse_str("DB_DRIVER", "NULL", "NULL", fail_if_empty=True)
        self.parse_str("SQLITE_DB_PATH", "sqlite_database", "filename", fail_if_empty=False)
        self.parse_str("HEADERS_FROM_EMAIL", "headers", "from", False, "")
        self.parse_str("DISCORD_TOKEN", "discord", "token", True)
        self.parse_str("CCP_CLIENT_ID", "ccp_developer", "client_id", True)
        self.parse_str("CCP_SECRET_KEY", "ccp_developer", "secret_key", True)
        self.parse_str("CCP_CALLBACK_URL", "ccp_developer", "callback_url", False,
                       "https://github.eveinsight.net/Insight/callback")
        self.parse_bool("CLEAR_TOKEN_TABLE_ON_ERROR", "NULL", "NULL", False, "FALSE", True)
        self.parse_str("DISCORDBOTS_APIKEY", "discordbots.org", "discordbots_apikey", False, "", True)
        self.parse_bool("INSIGHT_STATUS_CPUMEM", "NULL", "NULL", False, "TRUE", True)
        self.parse_bool("INSIGHT_STATUS_FEEDCOUNT", "NULL", "NULL", False, "TRUE", True)
        self.parse_bool("INSIGHT_STATUS_TIME", "NULL", "NULL", False, "TRUE", True)
        self.parse_int("LIMITER_GLOBAL_SUSTAIN_TICKETS", "NULL", "NULL", False, 9000, True)
        self.parse_int("LIMITER_GLOBAL_SUSTAIN_INTERVAL", "NULL", "NULL", False, 3600, True)
        self.parse_int("LIMITER_GLOBAL_BURST_TICKETS", "NULL", "NULL", False, 25, True)
        self.parse_int("LIMITER_GLOBAL_BURST_INTERVAL", "NULL", "NULL", False, 10, True)
        self.parse_int("LIMITER_DM_SUSTAIN_TICKETS", "NULL", "NULL", False, 1800, True)
        self.parse_int("LIMITER_DM_SUSTAIN_INTERVAL", "NULL", "NULL", False, 3600, True)
        self.parse_int("LIMITER_DM_BURST_TICKETS", "NULL", "NULL", False, 5, True)
        self.parse_int("LIMITER_DM_BURST_INTERVAL", "NULL", "NULL", False, 10, True)
        self.parse_int("LIMITER_GUILD_SUSTAIN_TICKETS", "NULL", "NULL", False, 9000, True)
        self.parse_int("LIMITER_GUILD_SUSTAIN_INTERVAL", "NULL", "NULL", False, 3600, True)
        self.parse_int("LIMITER_GUILD_BURST_TICKETS", "NULL", "NULL", False, 25, True)
        self.parse_int("LIMITER_GUILD_BURST_INTERVAL", "NULL", "NULL", False, 10, True)
        self.parse_int("LIMITER_CHANNEL_SUSTAIN_TICKETS", "NULL", "NULL", False, 1800, True)
        self.parse_int("LIMITER_CHANNEL_SUSTAIN_INTERVAL", "NULL", "NULL", False, 3600, True)
        self.parse_int("LIMITER_CHANNEL_BURST_TICKETS", "NULL", "NULL", False, 5, True)
        self.parse_int("LIMITER_CHANNEL_BURST_INTERVAL", "NULL", "NULL", False, 10, True)
        self.parse_int("LIMITER_USER_SUSTAIN_TICKETS", "NULL", "NULL", False, 320, True)
        self.parse_int("LIMITER_USER_SUSTAIN_INTERVAL", "NULL", "NULL", False, 3600, True)
        self.parse_int("LIMITER_USER_BURST_TICKETS", "NULL", "NULL", False, 4, True)
        self.parse_int("LIMITER_USER_BURST_INTERVAL", "NULL", "NULL", False, 45, True)
        self.parse_int("METRIC_LIMITER_MAX", "NULL", "NULL", False, 10, True)
        self.parse_str("REDIS_HOST", "NULL", "NULL", False, "", True)
        self.parse_int("REDIS_PORT", "NULL", "NULL", False, 6379, True)
        self.parse_str("REDIS_PASSWORD", "NULL", "NULL", False, "", True)
        self.parse_int("REDIS_DB", "NULL", "NULL", False, 0, True)
        self.parse_int("REDIS_TIMEOUT", "NULL", "NULL", False, 5, True)
        self.parse_bool("REDIS_SSL", "NULL", "NULL", False, "FALSE", True)
        self.parse_bool("REDIS_PURGE", "NULL", "NULL", False, "TRUE", True)
        self.parse_int("REDIS_CONNECTIONS_MIN", "NULL", "NULL", False, 50, True)
        self.parse_int("REDIS_CONNECTIONS_MAX", "NULL", "NULL", False, 100, True)
        self.parse_str("POSTGRES_HOST", "NULL", "NULL", fail_if_empty=False, nonotify=True)
        self.parse_int("POSTGRES_PORT", "NULL", "NULL", fail_if_empty=False, fallback_val=5432, nonotify=True)
        self.parse_str("POSTGRES_USER", "NULL", "NULL", fail_if_empty=False, nonotify=True)
        self.parse_str("POSTGRES_PASSWORD", "NULL", "NULL", fail_if_empty=False, nonotify=True)
        self.parse_str("POSTGRES_DB", "NULL", "NULL", fail_if_empty=False, nonotify=True)
        self.parse_int("POSTGRES_POOLSIZE", "NULL", "NULL", fail_if_empty=False, fallback_val=25, nonotify=True)
        self.parse_int("POSTGRES_POOLOVERFLOW", "NULL", "NULL", fail_if_empty=False, fallback_val=10, nonotify=True)
        self.parse_int("SUBSYSTEM_CACHE_THREADS", "NULL", "NULL", False, 8, True)
        self.parse_bool("SUBSYSTEM_CACHE_LASTSHIP_PRECACHE", "NULL", "NULL", False, "FALSE", True)
        self.parse_int("SUBSYSTEM_CACHE_LASTSHIP_TTL", "NULL", "NULL", False, 7200, True)
        self.parse_int("CRON_SYNCCONTACTS", "NULL", "NULL", False, 32400, True)
        self.parse_list("INSIGHT_ADMINS", "NULL", "NULL", False, "", False)
        self.parse_list("8BALL_RESPONSES", "NULL", "NULL", False, "Yes;No;Maybe", True)
        self.parse_int("DEFAULT_THREAD_COUNT", "NULL", "NULL",  False, 25, True)
        self.parse_str("ZK_REDISQ_URL", "NULL", "NULL", False, "https://redisq.zkillboard.com/listen.php", True)
        self.parse_str("ZK_WS_URL", "NULL", "NULL", False, "wss://zkillboard.com/websocket/", True)
        self.parse_bool("ZK_ID_RESET", "NULL", "NULL", False, "FALSE", True)
        self.parse_int("REIMPORT_LOCATIONS_MINUTES", "NULL", "NULL", False, 43200, True)  # 30 days
        self.parse_int("REIMPORT_TYPES_MINUTES", "NULL", "NULL", False, 21600, True) #15 days
        self.parse_int("REIMPORT_GROUPS_MINUTES", "NULL", "NULL", False, 14400, True) #10 days
        self.parse_int("REIMPORT_CATEGORIES_MINUTES", "NULL", "NULL", False, 14400, True) #10 days
        self.parse_int("REIMPORT_STARGATES_MINUTES", "NULL", "NULL", False, 7200, True) #5 days
        self.parse_int("REIMPORT_SYSTEMS_MINUTES", "NULL", "NULL", False, 21600, True)  # 15 days
        self.parse_int("REIMPORT_CONSTELLATIONS_MINUTES", "NULL", "NULL", False, 14400, True)  # 10 days
        self.parse_int("REIMPORT_REGIONS_MINUTES", "NULL", "NULL", False, 14400, True)  # 10 days
        self.parse_int("REIMPORT_CHARACTERS_MINUTES", "NULL", "NULL", False, 43200, True)  # 30 days
        self.parse_int("REIMPORT_CORPORATIONS_MINUTES", "NULL", "NULL", False, 21600, True)  # 15 days
        self.parse_int("REIMPORT_ALLIANCES_MINUTES", "NULL", "NULL", False, 21600, True)  # 15 days
        self.parse_bool("WEBSERVER_ENABLED", "NULL", "NULL", False, "FALSE", True)
        self.parse_str("WEBSERVER_INTERFACE", "NULL", "NULL", False, "127.0.0.1", True)
        self.parse_int("WEBSERVER_PORT", "NULL", "NULL", False, 8080, True)
        self.parse_str("CALLBACK_REDIRECT_SUCCESS", "NULL", "NULL", False, "", True)
