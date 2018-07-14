from .base_objects import *
from . import characters,corporations,alliances,types,systems
import requests


class name_resolve(name_only):
    @classmethod
    def post_url(cls):
        return "https://esi.evetech.net/latest/universe/names/?datasource=tranquility"

    @classmethod
    def get_headers(cls):
        return {
            'User-Agent': "InsightDiscordKillfeeds https://github.com/Nathan-LS/Insight Maintainer:Nathan nathan@nathan-s.com"}

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
        missing_object_dict = {}
        for row in cls.__get_objects_with_missing_names(service_module):
            missing_object_dict[row.get_id()] = row
        id_keys = list(missing_object_dict.keys())
        id_keys = list(set(id_keys) - set(error_ids))
        for id_list in cls.split_lists(id_keys,cls.missing_id_chunk_size()):
            try:
                response = requests.post(url=cls.post_url(), headers=cls.get_headers(), json=id_list, timeout=3)
                if response.status_code == 200:
                    for search_result in response.json():
                        selected_item = missing_object_dict.get(search_result.get('id'))
                        if selected_item is not None:
                            selected_item.set_name(search_result.get('name'))
                else:
                    ids_404.extend(id_list)
            except:
                ids_404.extend(id_list)
        try:
            db.commit()
        except Exception as ex:
            print(ex)
            db.rollback()
        finally:
            db.close()
            ids_404.extend(error_ids)
            return ids_404
