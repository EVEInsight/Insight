import service
import database.db_tables as dbRow
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sys


class static_data_import(object):
    def __init__(self, service_module,import_all=False):
        assert isinstance(service_module,service.ServiceModule)
        self.service = service_module
        if import_all:
            self.sde_importer()
            self.load_data_sde()
            self.load_indexes()
            self.load_api()
            self.engine.dispose()
        else:
            print("Skipping API static data import. This is not recommended.")

    def sde_importer(self):
        try:
            sdeBase = automap_base()
            self.engine = create_engine("sqlite:///{}".format(self.service.cli_args.sde_db), connect_args={'timeout':2775},echo=False)
            sdeBase.prepare(self.engine, reflect=True)
            self.sde_session = Session(self.engine)
            self.regions = sdeBase.classes.mapRegions
            self.constellations = sdeBase.classes.mapConstellations
            self.systems = sdeBase.classes.mapSolarSystems
            self.categories = sdeBase.classes.invCategories
            self.groups = sdeBase.classes.invGroups
            self.types = sdeBase.classes.invTypes
            self.locations = sdeBase.classes.mapDenormalize
            self.stargate_names = sdeBase.classes.invNames
        except Exception as ex:
            print("An error occurred when loading the SDE. Make sure you have downloaded and placed it correctly\n{}".format(ex))
            sys.exit(1)

    def load_data_sde(self):
        tb_systems.import_all_sde(self.service,self.sde_session,self.systems)
        tb_constellations.import_all_sde(self.service,self.sde_session,self.constellations)
        tb_regions.import_all_sde(self.service,self.sde_session,self.regions)
        tb_categories.import_all_sde(self.service,self.sde_session,self.categories)
        tb_groups.import_all_sde(self.service,self.sde_session,self.groups)
        tb_types.import_all_sde(self.service,self.sde_session,self.types)
        tb_locations.import_all_sde(self.service,self.sde_session,self.locations)
        tb_locations.import_stargates(self.service, self.sde_session, self.stargate_names)

    def load_indexes(self):
        dbRow.tb_regions.api_import_all_ids(self.service)
        dbRow.tb_constellations.api_import_all_ids(self.service)
        dbRow.tb_systems.api_import_all_ids(self.service)
        dbRow.tb_categories.api_import_all_ids(self.service)
        dbRow.tb_groups.api_import_all_ids(self.service)

    def load_api(self):
        dbRow.tb_types.api_import_all_ids(self.service)
        dbRow.tb_regions.api_mass_data_resolve(self.service)
        dbRow.tb_constellations.api_mass_data_resolve(self.service)
        dbRow.tb_systems.api_mass_data_resolve(self.service)
        dbRow.tb_categories.api_mass_data_resolve(self.service)
        dbRow.tb_groups.api_mass_data_resolve(self.service)


from database.db_tables import *
