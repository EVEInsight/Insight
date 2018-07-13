from swagger_client.rest import ApiException
import swagger_client
from sqlalchemy.orm import scoped_session, Session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import *
from sqlalchemy import *
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from multiprocessing.pool import ThreadPool
from database.db_tables import Base as dec_Base
import datetime
from typing import List
from dateutil.parser import parse as dateTimeParser


class table_row(object):
    def get_id(self):
        raise NotImplementedError

    def load_fk_objects(self):
        pass

    @staticmethod
    def get_configuration():
        configuration = swagger_client.Configuration()
        return configuration

    @staticmethod
    def get_api(configuration):
        raise NotImplementedError
        #return swagger_client.SkillsApi(swagger_client.ApiClient(configuration))

    @classmethod
    def get_response(cls,api):
        raise NotImplementedError
        # return api.get_characters_character_id_attributes(self.character_id,datasource='tranquility',token=token)

    @classmethod
    def primary_key_row(cls):
        raise NotImplementedError

    @classmethod
    def get_row(cls,id, service_module):
        db: Session = service_module.get_session()
        try:
            __row = db.query(cls).filter(cls.primary_key_row() == id).one()
            return __row
        except NoResultFound:
            __row = cls(id)
            return __row


class index_api_updating(table_row):
    @classmethod
    def api_import_all_ids(cls, service_module):
        try:
            __id_list = cls.__index_get_response(cls.__index_get_api(cls.get_configuration()))
            print("Found {} of object {} in API indexes.".format(str(len(__id_list)),cls.__name__))
            db: Session = service_module.get_session()
            for object_id in list(set(__id_list)-set([i[0] for i in db.query(cls.primary_key_row()).all()])):
                db.merge(cls(object_id))
            try:
                db.commit()
            except Exception as ex:
                print(ex)
                db.rollback()
            db.close()
        except ApiException as ex:
            print(ex)
        except Exception as ex:
            print(ex)

    @classmethod
    def index_swagger_api_call(cls, api, **kwargs):
        raise NotImplementedError
        #return api.get_universe_groups_with_http_info(**kwargs)

    @classmethod
    def __index_get_api(cls, configuration):
        return swagger_client.UniverseApi(swagger_client.ApiClient(configuration))

    @classmethod
    def __index_get_response(cls, api):
        r = cls.index_swagger_api_call(api, datasource='tranquility')
        number_pages = r[2].get("X-Pages")
        if number_pages is None:
            return r[0]
        else:
            r_items = [] + r[0]
            __index = 2
            while int(number_pages) >= __index:
                r_items += cls.index_swagger_api_call(api, page=__index, datasource='tranquility')[0]
                __index += 1
            return r_items


class individual_api_pulling(table_row):
    @hybrid_property
    def need_api(self):
        raise NotImplementedError

    @need_api.expression
    def need_api(cls):
        raise NotImplementedError

    def api_download(self):
        try:
            return self.get_response(self.get_api(self.get_configuration()), datasource='tranquility',
                                     if_none_match=str(self.api_ETag))
        except ApiException as ex:
            return None
        except Exception as ex:
            return None

    def api_import(self, data):
        try:
            self.process_body(data[0].to_dict())
            self.process_headers(data[2])
            self.load_fk_objects()
        except Exception as ex:
            print(ex)

    def process_body(self,response):
        raise NotImplementedError

    @staticmethod
    def get_api(configuration):
        return swagger_client.UniverseApi(swagger_client.ApiClient(configuration))

    def get_response(self, api, **kwargs):
        raise NotImplementedError

    def process_headers(self, response):
        try:
            self.api_ETag = response.get("Etag")
            self.api_Expires = dateTimeParser(response.get("Expires"))
            self.api_Last_Modified = dateTimeParser(response.get("Last-Modified"))
        except Exception as ex:
            print(ex)

    @classmethod
    def missing_api_objects(cls, service_module):
        db: Session = service_module.get_session()
        return db.query(cls).filter(cls.need_api).all()

    @classmethod
    def __helper_call_api_populate(cls,row_object):
        return_dict = {}
        return_dict["id"] = row_object.get_id()
        return_dict["data"] = row_object.api_download()
        return return_dict

    @classmethod
    def api_mass_data_resolve(cls, service_module):
        db:Session = service_module.get_session()
        __rows = cls.missing_api_objects(service_module)
        print("Need to update data on {} {} objects".format(str(len(__rows)),cls.__name__)) if len(__rows) > 0 else None
        try:
            pool = ThreadPool(20)
            results = pool.map(cls.__helper_call_api_populate, __rows)
            pool.close()
            pool.join()
            db.close()
            for item in results:
                try:
                    if item.get("data") is not None and item.get("id") is not None:
                        __row = cls(item.get("id"))
                        __row.api_import(item.get("data"))
                        db.merge(__row)
                        db.commit()
                except Exception as ex:
                    db.rollback()
                    print(ex)
                db.close()
        except Exception as ex:
            print(ex)
        remaining = len(cls.missing_api_objects(service_module))
        db.close()
        if remaining > 0:
            print("{} remaining {} with data missing after ESI calls.".format(str(remaining),cls.__name__))
            return remaining
        else:
            return remaining


class name_only(table_row):

    @classmethod
    def make_row(cls,id):
        return cls(id)

    def set_name(self, api_name):
        raise NotImplementedError

    def get_name(self):
        raise NotImplementedError

    @hybrid_property
    def need_name(self):
        raise NotImplementedError

    @staticmethod
    def get_api(configuration):
        return swagger_client.UniverseApi(swagger_client.ApiClient(configuration))

    @classmethod
    def get_response(cls, api, **kwargs):
        return api.post_universe_names(**kwargs, datasource='tranquility')

    @classmethod
    def missing_id_chunk_size(cls)->int:
        return 1000

    @classmethod
    def missing_name_objects(cls, service_module):
        db: Session = service_module.get_session()
        return db.query(cls).filter(cls.need_name == True).all()

    @staticmethod
    def split_lists(list_item, chunk_size):
        for i in range(0,len(list_item),chunk_size):
            yield list_item[i:i+chunk_size]







