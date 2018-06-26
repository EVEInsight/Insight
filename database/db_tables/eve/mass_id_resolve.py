from .base_objects import name_only
from discord_bot import discord_options
from . import systems,characters,corporations,alliances

class id_resolve(name_only):
    @classmethod
    def get_response(cls, api, **kwargs):
        return api.post_universe_ids(**kwargs, datasource='tranquility',user_agent="InsightDiscordBot")

    @classmethod
    def make_options(cls,option_mapper,search_str):
        def make_categories(options:discord_options.mapper_index,resp,db_row:systems.Systems,header_str):
            if resp is not None:
                options.add_header_row(header_str)
                for i in resp:
                    try:
                        options.add_option(discord_options.option_returns_object("{}".format(i.name),return_object=db_row(i.id)))
                    except Exception as ex:
                        print("ex")
        assert isinstance(option_mapper,discord_options.mapper_index)
        option_mapper.set_main_header("Select from the following:")
        resp = cls.get_response(cls.get_api(cls.get_configuration()),names=[str(search_str)])
        make_categories(option_mapper,resp.alliances,alliances.Alliances,"Alliances")
        make_categories(option_mapper, resp.corporations, corporations.Corporations,"Corporations")
        make_categories(option_mapper, resp.characters, characters.Characters,"Pilots")
        return option_mapper