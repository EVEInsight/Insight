from . import Base_Feed
import discord
from discord_bot import discord_options as dOpt
from database.db_tables import id_resolver
from functools import partial
from sqlalchemy.orm import *
from sqlalchemy import *
from typing import List


class Options_EnFeed(Base_Feed.base_activefeed):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, enFeed.enFeed)
        super().__init__(insight_channel)

    async def InsightOptionRequired_add(self, message_object:discord.Message):
        """Add tracked entities  - Add an entity (pilot, corp, or alliance) to post their involved kms. You can add more than 1 tracking entities to a channel if you wish."""

        def make_options(search_str) -> dOpt.mapper_index:
            __options = dOpt.mapper_index(self.cfeed.discord_client, message_object, timeout_seconds=45)
            __options.set_main_header("Select the entity you wish to add.")
            db: Session = self.cfeed.service.get_session()

            def header_make(row_list:List[tb_alliances],header_text):
                if len(row_list) > 0:
                    __options.add_header_row(header_text)
                    for i in row_list:
                        __options.add_option(dOpt.option_returns_object(name=i.get_name(), return_object=i))
            try:
                header_make(db.query(tb_alliances).filter(tb_alliances.alliance_name.ilike("%{}%".format(search_str))).all(),"Alliances")
                header_make(db.query(tb_corporations).filter(tb_corporations.corporation_name.ilike("%{}%".format(search_str))).all(),"Corporations")
                header_make(db.query(tb_characters).filter(tb_characters.character_name.ilike("%{}%".format(search_str))).all(),"Pilots")
                __options.add_header_row("Additional Options")
                __options.add_option(dOpt.option_returns_object("Search again", return_object=None))
            except Exception as ex:
                print(ex)
                db.rollback()
            finally:
                db.close()
                return __options

        __search = dOpt.mapper_return_noOptions(self.cfeed.discord_client, message_object, timeout_seconds=60)
        __search.set_main_header("Enter the name of an entity you wish to track in this feed.\n\n"
                                 "An entity is a pilot, corporation, or alliance in which this channel "
                                 "will streams kms involving.")
        __search.set_footer_text("Enter a name. Note: partial names are accepted: ")
        __selected_option = None
        while __selected_option is None:
            __search_name = await __search()
            __func = partial(id_resolver.api_mass_id_resolve,self.cfeed.service,__search_name)
            await self.cfeed.discord_client.loop.run_in_executor(None, __func) #lookup name from eve api first and add to db
            __found_results = await self.cfeed.discord_client.loop.run_in_executor(None,partial(make_options,__search_name))
            __selected_option = await __found_results()
        function_call = partial(tb_channels.commit_list_entry,__selected_option,self.cfeed.channel_id,self.cfeed.service)
        __code = await self.cfeed.discord_client.loop.run_in_executor(None, function_call)
        await self.response_code_action(message_object, __code)

    async def InsightOption_remove(self,message_object:discord.Message):
        """Remove tracking  - Removes tracking of km involvement for a pilot, corp, or alliance."""

        def remove_en(row):
            db: Session = self.cfeed.service.get_session()
            try:
                db.delete(row)
                db.commit()
                return "ok"
            except Exception as ex:
                print(ex)
                return "An error occurred when attempting to remove this entity from the entity feed."
            finally:
                db.close()

        def get_options():
            db: Session = self.cfeed.service.get_session()
            _options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, message_object, timeout_seconds=70)
            _options.set_main_header("Remove tracking for an entity")
            try:
                for pilot in db.query(tb_Filter_characters).filter(
                        tb_Filter_characters.channel_id == self.cfeed.channel_id).all():
                    _options.add_option(
                        dOpt.option_returns_object(name=pilot.object_item.get_name(), return_object=pilot))
                for corp in db.query(tb_Filter_corporations).filter(
                        tb_Filter_corporations.channel_id == self.cfeed.channel_id).all():
                    _options.add_option(
                        dOpt.option_returns_object(name=corp.object_item.get_name(), return_object=corp))
                for ali in db.query(tb_Filter_alliances).filter(
                        tb_Filter_alliances.channel_id == self.cfeed.channel_id).all():
                    _options.add_option(dOpt.option_returns_object(name=ali.object_item.get_name(), return_object=ali))
            except Exception as ex:
                print(ex)
            finally:
                db.close()
            return _options

        _options = await self.cfeed.discord_client.loop.run_in_executor(None, get_options)
        _row = await _options()
        _resp = await self.cfeed.discord_client.loop.run_in_executor(None, partial(remove_en, _row))
        await self.response_code_action(message_object, _resp)

    async def InsightOptionRequired_tracktype(self, message_object:discord.Message):
        """Show losses/kills  - Set the feed to one of three modes for tracked entities: show losses only, show kills only, show both kills and losses"""
        def set_mode(option):
            db:Session = self.cfeed.service.get_session()
            try:
                __row:tb_enfeed = db.query(tb_enfeed).filter(tb_enfeed.channel_id==self.cfeed.channel_id).one()
                __row.show_mode = option
                db.merge(__row)
                db.commit()
                return "ok"
            except Exception as ex:
                print(ex)
                return "An error occurred when attempting to set channel mode: {}".format(str(ex))
            finally:
                db.close()

        __options = dOpt.mapper_index(self.cfeed.discord_client, message_object, timeout_seconds=45)
        __options.set_main_header("Select the KM viewing mode for this entity feed.")
        __options.add_option(dOpt.option_returns_object(
            name="Show losses only   - Only losses involving your tracked entities will be posted",
            return_object=enum_kmType.losses_only))
        __options.add_option(dOpt.option_returns_object(
            name="Show kills only   - Only kills where your tracked entities were attackers will be posted",
            return_object=enum_kmType.kills_only))
        __options.add_option(dOpt.option_returns_object(
            name="Show kills and losses   - Both kills and losses involving feed tracked entities will be posted",
            return_object=enum_kmType.show_both))
        __selected_option = await __options()
        __code = await self.cfeed.discord_client.loop.run_in_executor(None,partial(set_mode,__selected_option))
        await self.response_code_action(message_object, __code)



from .. import enFeed
from database.db_tables import *