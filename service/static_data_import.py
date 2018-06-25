import service
import database.db_tables as dbRow


class static_data_import(object):
    def __init__(self, service_module):
        assert isinstance(service_module,service.ServiceModule)
        self.service = service_module

    def load_data(self):
        dbRow.tb_regions.api_import_all_ids(self.service)
        dbRow.tb_constellations.api_import_all_ids(self.service)
        dbRow.tb_systems.api_import_all_ids(self.service)
        dbRow.tb_categories.api_import_all_ids(self.service)
        dbRow.tb_groups.api_import_all_ids(self.service)
        # dbRow.tb_types.api_import_all_ids(self.service)
        # dbRow.tb_regions.api_mass_data_resolve(self.service)
        # dbRow.tb_constellations.api_mass_data_resolve(self.service)
        # dbRow.tb_systems.api_mass_data_resolve(self.service)
        # dbRow.tb_categories.api_mass_data_resolve(self.service)
        # dbRow.tb_groups.api_mass_data_resolve(self.service)

