from .base_objects import *
from . import characters,corporations,alliances,types,systems
import requests
import traceback
import InsightLogger


class name_resolve(name_only):
    @classmethod
    def post_url(cls):
        return "https://esi.evetech.net/latest/universe/names/?datasource=tranquility"

    @classmethod
    def __get_objects_with_missing_names(cls,service_module):
        __missing_objects = []
        __missing_objects += characters.Characters.missing_name_objects(service_module)
        __missing_objects += corporations.Corporations.missing_name_objects(service_module)
        __missing_objects += alliances.Alliances.missing_name_objects(service_module)
        __missing_objects += types.Types.missing_name_objects(service_module)
        __missing_objects += characters.Characters.missing_name_objects(service_module)
        __missing_objects += systems.Systems.missing_name_objects(service_module)
        return __missing_objects

    @classmethod
    def api_mass_name_resolve(cls, service_module, error_ids=[]):
        ids_404 = []
        db: Session = service_module.get_session()
        try:
            missing_object_dict = {}
            for row in cls.__get_objects_with_missing_names(service_module):
                missing_object_dict[row.get_id()] = row
            id_keys = list(missing_object_dict.keys())
            id_keys = list(set(id_keys) - set(error_ids))
            for id_list in cls.split_lists(id_keys, cls.missing_id_chunk_size()):
                lg = InsightLogger.InsightLogger.get_logger('ZK.names', 'ZK.log', child=True)
                lg.info('Processing name chunk of size {} from {} total missing names.'.format(len(id_list), len(id_keys)))
                try:
                    response = requests.post(url=cls.post_url(), headers=service_module.get_headers(lib_requests=True),
                                             json=id_list, timeout=3)
                    if response.status_code == 200:
                        for search_result in response.json():
                            selected_item = missing_object_dict.get(search_result.get('id'))
                            if selected_item is not None:
                                selected_item.set_name(search_result.get('name'))
                    else:
                        lg.warning('Response {} Headers: {} Body: {} IDs: {}'.
                                    format(response.status_code, response.headers, response.json(), str(id_list)))
                        ids_404.extend(id_list)
                except requests.exceptions.Timeout:
                    lg.info('Timeout.')
                    ids_404.extend(id_list)
                except Exception as ex:
                    lg.exception(ex)
                    print('Error: {} when resolving char names.'.format(ex))
                    ids_404.extend(id_list)
            db.commit()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
        finally:
            db.close()
            ids_404.extend(error_ids)
            return ids_404
