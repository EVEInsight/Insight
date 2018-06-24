from service.service import *
from sqlalchemy.orm import Session
import swagger_client
from swagger_client.rest import ApiException
from swagger_client import Configuration
from multiprocessing.pool import ThreadPool


class static_data_import(object):
    def __init__(self, service_module):
        self.service: service_module = service_module

    def load_data(self,system_id):
        row = tb_systems(system_id)
        __status = row.api_populate()
        if __status == 200:
            print("Downloaded info for system: {}".format(row.name))
        return row

    def missing_list(self,list_in_db,list_api):
        assert isinstance(list_in_db,list)
        assert isinstance(list_api,list)
        return list(set(list_api)-set(list_in_db))

    def import_systems(self):
        db: Session = self.service.get_session()
        api = swagger_client.UniverseApi(swagger_client.ApiClient(swagger_client.Configuration()))
        api_systems = api.get_universe_systems()
        total_attempts = 0
        while len(self.missing_list([s.system_id for s in db.query(tb_systems.system_id).filter(tb_systems.name != None).all()],api_systems)) > 0 and total_attempts <=5 :
            missing_systems = self.missing_list([s.system_id for s in db.query(tb_systems.system_id).filter(tb_systems.name != None).all()],api_systems)
            print("Missing data for {} of {} total systems".format(str(len(missing_systems)),str(len(api_systems))))
            pool = ThreadPool(20)
            results = pool.map(self.load_data,missing_systems)
            pool.close()
            pool.join()
            for i in results:
                if isinstance(i,tb_systems):
                    db.merge(i)
            db.commit()
            total_attempts +=1

