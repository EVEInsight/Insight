from database.tables import *
from database.setup_db import setup_database
from sqlalchemy.orm import scoped_session, Session
from service.static_data_import import static_data_import
from service.channel_manager import Channel_manager
from service.zk import zk
import argparse
import configparser
from threading import Lock

class service_module(object):
    def __init__(self):
        self.config_file = configparser.ConfigParser()
        self.cli_args = self.__read_cli_args()
        self.config_file.read(self.__read_config_file())
        self.__sc_session: scoped_session = setup_database().get_scoped_session()
        #self.static_data_import = static_data_import(self)
        #self.static_data_import.import_systems()
        # tb_regions.api_import_all_ids(self)
        # tb_constellations.api_import_all_ids(self)
        # tb_systems.api_import_all_ids(self)
        # tb_categories.api_import_all_ids(self)
        # tb_groups.api_import_all_ids(self)
        # tb_types.api_import_all_ids(self)
        # tb_regions.api_mass_data_resolve(self)
        # tb_constellations.api_mass_data_resolve(self)
        # tb_systems.api_mass_data_resolve(self)
        # tb_categories.api_mass_data_resolve(self)
        # tb_groups.api_mass_data_resolve(self)
        self.channel_manager = Channel_manager(self)
        self.zk_obj = zk(self)

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