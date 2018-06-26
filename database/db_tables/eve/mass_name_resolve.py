from .base_objects import *
from . import characters,corporations,alliances,types,systems


class name_resolve(name_only):
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
    def api_mass_name_resolve(cls, service_module):
        db: Session = service_module.get_session()
        missing_object_dict = {}
        for row in cls.__get_objects_with_missing_names(service_module):
            missing_object_dict[row.get_id()] = row
        id_keys = list(missing_object_dict.keys())
        for id_list in cls.split_lists(id_keys,cls.missing_id_chunk_size()):
            try:
                response = cls.get_response(cls.get_api(cls.get_configuration()), ids=id_list)
                for search_result in response:
                    selected_item = missing_object_dict.get(search_result.id)
                    if selected_item is not None:
                        selected_item.set_name(search_result.name)
            except Exception as ex:
                print(ex)
        try:
            db.commit()
        except Exception as ex:
            print(ex)
            db.rollback()
        db.close()
