from sqlalchemy.orm import scoped_session, Session
from . import channel_manager as cm
from . import zk as zk
from . import static_data_import as static_data
import database
import argparse
import configparser


class service_module(object):
    def __init__(self):
        self.config_file = configparser.ConfigParser()
        self.cli_args = self.__read_cli_args()
        self.config_file.read(self.__read_config_file())
        self.__sc_session: scoped_session = database.setup_database().get_scoped_session()
        self.static_data_import = static_data.static_data_import(self)
        #self.static_data_import.load_data()
        self.channel_manager = cm.Channel_manager(self)
        self.zk_obj = zk.zk(self)

    def __read_cli_args(self):
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
        return parser.parse_args()

    def __read_config_file(self):
        try:
            with open(self.cli_args.config, 'r') as f:
                return self.cli_args.config
        except FileNotFoundError:
            print("The config file '{0}' could not be found. Try renaming the file 'default-config.ini' to '{0}'".format(str(self.cli_args.config)))
            exit(1)

    def get_session(self)-> Session:
        """

        :rtype: Session
        """
        session_object: Session = self.__sc_session()
        assert isinstance(session_object,Session)
        return session_object

    def close_session(self):
        self.__sc_session.remove()