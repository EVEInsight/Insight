from . import Base_Feed
import discord
from discord_bot import discord_options as dOpt
from database.db_tables import id_resolver
from functools import partial
from sqlalchemy.orm import *
from sqlalchemy import *
from typing import List
import InsightExc
from InsightUtilities import LimitManager


class Options_EnFeed(Base_Feed.base_activefeed):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, enFeed.enFeed)
        super().__init__(insight_channel)
        self.pod_group_ids = [29]

    def yield_options(self):
        yield (self.InsightOptionRequired_add, True)
        yield (self.InsightOption_remove, False)
        yield (self.InsightOptionRequired_tracktype, True)
        yield (self.InsightOptionRequired_trackpods, True)
        yield (self.InsightOption_minValue, False)
        yield from super().yield_options()

    async def InsightOptionRequired_add(self, message_object:discord.Message):
        """Add a new tracked entity  - Add an entity (pilot, corp, or alliance) to track involved PvP activity. You can add more than 1 entity to a channel."""

        def make_options(search_str) -> dOpt.mapper_index:
            __options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, message_object)
            __options.set_main_header(
                "Select the entity you wish to add.\nNote: Additional entities can be added or removed after feed creation by running the ‘!settings’ command.")
            db: Session = self.cfeed.service.get_session()

            def header_make(row_list:List[tb_alliances],header_text):
                if len(row_list) > 0:
                    __options.add_header_row(header_text)
                    for i in row_list:
                        __options.add_option(dOpt.option_returns_object(name=i.get_name(), return_object=i))
            try:
                header_make(SearchHelper.search(db, tb_alliances, tb_alliances.alliance_name, search_str), "Alliances")
                header_make(SearchHelper.search(db, tb_corporations, tb_corporations.corporation_name, search_str), "Corporations")
                header_make(SearchHelper.search(db, tb_characters, tb_characters.character_name, search_str),"Pilots")
                __options.add_header_row("Additional Options")
                __options.add_option(dOpt.option_returns_object("Search again", return_object=None))
                return __options
            except Exception as ex:
                raise ex
            finally:
                db.close()

        __search = dOpt.mapper_return_noOptions(self.cfeed.discord_client, message_object)
        __search.set_main_header("Enter the name of an entity you wish to track.\n\n"
                                 "An entity is a pilot, corporation, or alliance.")
        __search.set_footer_text("Enter a name. Note: partial names are accepted: ")
        __selected_option = None
        while __selected_option is None:
            __search_name = await __search()
            if len(__search_name) <= 2:
                raise InsightExc.userInput.ShortSearchCriteria(min_length=3)
            __func = partial(id_resolver.api_mass_id_resolve,self.cfeed.service,__search_name)
            await self.cfeed.discord_client.loop.run_in_executor(None, __func) #lookup name from eve api first and add to db
            __found_results = await self.cfeed.discord_client.loop.run_in_executor(None,partial(make_options,__search_name))
            __selected_option = await __found_results()
        function_call = partial(tb_channels.commit_list_entry,__selected_option,self.cfeed.channel_id,self.cfeed.service)
        await self.cfeed.discord_client.loop.run_in_executor(None, function_call)
        await self.reload(message_object)

    async def InsightOption_remove(self,message_object:discord.Message):
        """Remove a tracked entity - Remove tracking of PvP activity for a previously added pilot, corp, or alliance."""
        def get_options():
            db: Session = self.cfeed.service.get_session()
            _options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, message_object)
            _options.set_main_header("Remove an entity from being tracked in this feed:")
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
        await self.delete_row(_row)
        await self.reload(message_object)

    async def InsightOptionRequired_tracktype(self, message_object:discord.Message):
        """Show losses/kills  - Set the feed to one of three modes: show losses only, show kills only, or show both kills and losses."""
        def set_mode(option):
            db:Session = self.cfeed.service.get_session()
            try:
                __row: tb_enfeed = db.query(tb_enfeed).filter(tb_enfeed.channel_id == self.cfeed.channel_id).one()
                __row.show_mode = option
                db.merge(__row)
                db.commit()
            except Exception as ex:
                print(ex)
                raise InsightExc.Db.DatabaseError
            finally:
                db.close()

        __options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, message_object)
        __options.set_main_header("Select the killmail viewing mode for this entity feed.")
        __options.add_option(dOpt.option_returns_object(
            name="Show kills and losses - Both kills and losses involving tracked entities will be posted.",
            return_object=enum_kmType.show_both))
        __options.add_option(dOpt.option_returns_object(
            name="Show kills only - Only kills where your tracked entities were attackers will be posted.",
            return_object=enum_kmType.kills_only))
        __options.add_option(dOpt.option_returns_object(
            name="Show losses only - Only losses involving your tracked entities will be posted.",
            return_object=enum_kmType.losses_only))
        __selected_option = await __options()
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(set_mode, __selected_option))
        await self.reload(message_object)

    async def InsightOptionRequired_trackpods(self, message_object: discord.Message):
        """Display POD(capsule) kills/losses - Set the feed to either ignore or display POD mails."""

        def set_mode(track_pods):
            db: Session = self.cfeed.service.get_session()
            try:
                if not track_pods:
                    for i in self.pod_group_ids:
                        __row: tb_Filter_groups = tb_Filter_groups.get_row(self.cfeed.channel_id, i, self.cfeed.service)
                        db.merge(__row)
                    db.commit()
                else:
                    for i in self.pod_group_ids:
                        tb_Filter_groups.get_remove(self.cfeed.channel_id, i, self.cfeed.service)
                    db.commit()
            except Exception as ex:
                print(ex)
                raise InsightExc.Db.DatabaseError
            finally:
                db.close()

        __options = dOpt.mapper_return_yes_no(self.cfeed.discord_client, message_object)
        __options.set_main_header("Do you want to track pod (capsule) kills/losses in this feed?")
        resp = await __options()
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(set_mode, resp))
        await self.reload(message_object)

    async def InsightOption_minValue(self, message_object: discord.Message):
        """Set minimum ISK value - Set the minimum ISK value for killmails."""

        def get_number(input_val: str):
            try:
                input_val = input_val.strip()
                num = "".join([c for c in input_val if c.isdigit() or c == '.'])
                n_modifier = "".join(a.casefold() for a in input_val if a.isalpha())
                num = float(num)
                if n_modifier.startswith('b'):
                    num = num * 1e+9
                elif n_modifier.startswith('m'):
                    num = num * 1e+6
                elif n_modifier.startswith('k'):
                    num = num * 1e+3
                else:
                    pass
                return num
            except:
                raise InsightExc.userInput.NotFloat

        def set_min_value(isk_val):
            db: Session = self.cfeed.service.get_session()
            try:
                row: tb_enfeed = db.query(tb_enfeed).filter(tb_enfeed.channel_id == self.cfeed.channel_id).one()
                row.minValue = isk_val
                db.merge(row)
                db.commit()
            except Exception as ex:
                print(ex)
                raise InsightExc.Db.DatabaseError
            finally:
                db.close()

        options = dOpt.mapper_return_noOptions(self.cfeed.discord_client, message_object)
        options.set_main_header("Set the minimum isk value for killmails. Mails below this value will not be posted. "
                                "Enter '0' for no limit.")
        options.set_footer_text("Enter a number. Examples: 500m, 10 billion, 500,000: ")
        resp = await options()
        val = get_number(resp)
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(set_min_value, val))
        await self.reload(message_object)
        async with (await LimitManager.cm_hp(message_object.channel)):
            await message_object.channel.send("Minimum ISK value is now set at: {:,.2f} ISK.".format(val))


from .. import enFeed
from database.db_tables import *