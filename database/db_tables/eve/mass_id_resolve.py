from .base_objects import name_only
from discord_bot import discord_options
from sqlalchemy.orm import Session
from swagger_client.rest import ApiException


class id_resolve(name_only):
    @classmethod
    def get_response(cls, api, **kwargs):
        return api.post_universe_ids(**kwargs, datasource='tranquility',user_agent="InsightDiscordBot")

    @classmethod
    def api_mass_id_resolve(cls,service_module,search_str):
        db: Session = service_module.get_session()

        def make_rows(item_list,row_init:tb_alliances):
            if item_list is not None:
                for i in item_list:
                    __row = row_init.make_row(i.id)
                    __row.set_name(i.name)
                    db.merge(__row)
        try:
            resp = cls.get_response(cls.get_api(cls.get_configuration()),names=[str(search_str)])
            try:
                make_rows(resp.alliances,tb_alliances)
                make_rows(resp.corporations,tb_corporations)
                make_rows(resp.characters,tb_characters)
                db.commit()
            except Exception as ex:
                print(ex)
                db.rollback()
            finally:
                db.close()
        except ApiException as ex:
            print(ex)
        service_module.close_session()


from ..eve import tb_characters,tb_corporations,tb_alliances