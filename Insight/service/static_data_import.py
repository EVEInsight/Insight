import service
import database.db_tables as dbRow
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sys
from InsightUtilities.StaticHelpers import Helpers
from datetime import datetime, timedelta
from dateutil.parser import parse as dateTimeParser
import traceback


class static_data_import(object):
    def __init__(self, service_module,import_all=False):
        assert isinstance(service_module,service.ServiceModule)
        self.service = service_module
        if import_all:
            self.reimport_static_data()
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
            self.stargates = sdeBase.classes.mapSolarSystemJumps
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
        tb_stargates.import_all_sde(self.service, self.sde_session, self.stargates)

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
        dbRow.tb_types.update_prices(self.service)

    def _query_reimport(self, table, threshold_config_key, meta_key, query):
        last_modified = dateTimeParser(Helpers.get_nested_value(tb_meta.get(meta_key),
                                                 str(datetime.utcnow()), "data", "value"))
        m = int(self.service.config.get(threshold_config_key))
        if m < 0:
            print("Skipping reimport on {} as it is disabled. This is not recommended as there can be outdated SDE "
                  "data and it's good practice to reimport SDE data at regular intervals.".format(table))
            return

        if m > 0:
            next_modify = last_modified + timedelta(minutes=m)
            if datetime.utcnow() < next_modify:
                return

        print("\n\nResetting some data on the {} table for reimport. Resets are scheduled to reimport data into "
              "this table every {} minutes. \nThe reset schedule can be adjusted by setting the \"{}\" environmental "
              "variable. Setting this variable to -1 disables the reimport."
              "\nExecuting SQL query: \"{}\"".format(table, m, threshold_config_key, query))
        db: Session = self.service.get_session()
        try:
            db.execute(query)
            db.commit()
        except Exception as ex:
            traceback.print_exc()
            print(ex)
            raise ex
        finally:
            db.close()

        if tb_meta.set(meta_key, {"value": str(datetime.utcnow())}):
            print("Cleaning table {} done!".format(table))
        else:
            print("Error when updating meta_key for {}".format(meta_key))
            sys.exit(1)

    def reimport_static_data(self):
        """clears potentially invalid data from database for a reimport from the SDE"""
        self._query_reimport("locations", "REIMPORT_LOCATIONS_MINUTES", "last_reimport_locations",
                             "UPDATE locations SET name = NULL, \"typeID\" = NULL, \"groupID\" = NULL, pos_x = NULL, pos_y = NULL, pos_z = NULL, radius = NULL;")
        self._query_reimport("types", "REIMPORT_TYPES_MINUTES", "last_reimport_types",
                             "UPDATE types SET type_name = NULL, group_id = NULL;")
        self._query_reimport("groups", "REIMPORT_GROUPS_MINUTES", "last_reimport_groups",
                             "UPDATE groups SET name = NULL, category_id = NULL;")
        self._query_reimport("categories", "REIMPORT_CATEGORIES_MINUTES", "last_reimport_categories",
                             "UPDATE categories SET name = NULL;")
        self._query_reimport("stargates", "REIMPORT_STARGATES_MINUTES", "last_reimport_stargates",
                             "DELETE FROM stargates;")
        self._query_reimport("systems", "REIMPORT_SYSTEMS_MINUTES", "last_reimport_systems",
                             "UPDATE systems SET name = NULL, constellation_id = NULL, pos_x = NULL, pos_y = NULL, pos_z = NULL;")
        self._query_reimport("constellations", "REIMPORT_CONSTELLATIONS_MINUTES", "last_reimport_constellations",
                             "UPDATE constellations SET name = NULL, region_id = NULL;")
        self._query_reimport("regions", "REIMPORT_REGIONS_MINUTES", "last_reimport_regions",
                             "UPDATE regions SET name = NULL;")
        self._query_reimport("characters", "REIMPORT_CHARACTERS_MINUTES", "last_reimport_characters",
                             "UPDATE characters SET character_name = NULL;")
        self._query_reimport("corporations", "REIMPORT_CORPORATIONS_MINUTES", "last_reimport_corporations",
                             "UPDATE corporations SET corporation_name = NULL;")
        self._query_reimport("alliances", "REIMPORT_ALLIANCES_MINUTES", "last_reimport_alliances",
                             "UPDATE alliances SET alliance_name = NULL;")

from database.db_tables import *
