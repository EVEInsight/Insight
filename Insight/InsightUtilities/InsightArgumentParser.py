import argparse


class InsightArgumentParser(object):
    @classmethod
    def get_cli_args(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("--config", "-c",
                            help="Specifies a config file other than the default 'config.ini' to run the program with",
                            default="config.ini")
        parser.add_argument("--debug_km","-km",
                            help="Start the application in debug mode to send kms starting at and above this id through all channel feeds.",
                            type=int)
        parser.add_argument("--force_ctime","-fc",
                            action="store_true",
                            help="If --debug_km is set, this flag will push kms to feeds with their time occurrence set to now.",
                            default=False)
        parser.add_argument("--debug_limit","-limit",
                            help="Sets the total limit of debug kms to push through feeds before exiting the program. Default is unlimited.",
                            type=int)
        parser.add_argument("--skip_api_import", "-noapi", action="store_true",
                            help="Skip startup API static data import check.", default=False)
        parser.add_argument("--websocket", "-ws", action="store_true",
                            help="Enable the experimental secondary ZK websocket connection.", default=False)
        parser.add_argument("--defer_tasks", "-defer", action="store_true",
                            help="Defers slow tasks to run later instead of at startup.", default=False)
        parser.add_argument("--sde_db","-sde",
                            help="Specifies the name of the SDE database file relative to main.py. Download and extract the "
                                 "sqlite-latest.sqlite file from https://www.fuzzwork.co.uk/dump/",
                            type=str, default="sqlite-latest.sqlite")
        parser.add_argument("--crash_recovery", "-cr", action="store_true",
                            help="Automatically reboot Insight in the event of an application crash.", default=False)
        parser.add_argument("--build-binary", "-b", action="store_true",
                            help="Utilize the Docker image to build a binary package of Insight.", default=False)
        parser.add_argument("--docker-init", "-d", action="store_true",
                            help="Initialize the Docker volume with the configuration and README files.", default=False)
        parser.add_argument("--auth", "-a", action="store_true",
                            help="Boot Insight in SSO token authorization code converter mode. Given an authorization "
                                 "token, Insight will provide a raw refresh_token. Mainly used for unit testing.",
                            default=False)
        return parser.parse_args()
