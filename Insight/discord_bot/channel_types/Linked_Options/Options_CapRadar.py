from . import Base_Feed
import discord
from functools import partial
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError
import InsightExc


class Options_CapRadar(Base_Feed.base_activefeed):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, capRadar.capRadar)
        super().__init__(insight_channel)
        self.super_ids = [30,659]
        self.capital_ids = [547, 485, 1538, 883]
        self.blops_ids = [898]

    def yield_options(self):
        yield (self.InsightOptionRequired_add, True)
        yield (self.InsightOption_remove, False)
        yield (self.InsightOptionRequired_supers, True)
        yield (self.InsightOptionRequired_capitals, True)
        yield (self.InsightOptionRequired_blops, True)
        yield (self.InsightOptionRequired_maxage, True)
        yield (self.InsightOption_sync, False)
        yield from super().yield_options()

    def mention_options(self,message_object,group_type):
        __options = discord_options.mapper_index(self.cfeed.discord_client, message_object)
        __options.set_main_header("Select the mention mode for this channel. On detected {} activity the bot "
                                  "can optionally mention @ here or @ everyone.\n\n"
                                  "Mention limit: 1 @ here or @ everyone per 15 minutes regardless of tracked "
                                  "group. If the limit is exceeded, the killmail will be posted without mentions.".format(
            group_type))
        __options.add_option(discord_options.option_returns_object("No mention", return_object=enum_mention.noMention))
        __options.add_option(discord_options.option_returns_object("@ here", return_object=enum_mention.here))
        __options.add_option(discord_options.option_returns_object("@ everyone", return_object=enum_mention.everyone))
        return __options

    def modify_groups(self,group_ids,mention_method,remove=False):
        db: Session = self.cfeed.service.get_session()
        try:
            if not remove:
                for i in group_ids:
                    __row: tb_Filter_groups = tb_Filter_groups.get_row(self.cfeed.channel_id,i,self.cfeed.service)
                    __row.mention = mention_method
                    db.merge(__row)
                db.commit()
            else:
                for i in group_ids:
                    tb_Filter_groups.get_remove(self.cfeed.channel_id,i,self.cfeed.service)
                db.commit()
        except Exception as ex:
            print(ex)
            raise InsightExc.Db.DatabaseError
        finally:
            db.close()

    async def InsightOptionRequired_add(self, message_object: discord.Message):
        """Add a new base system - Track targets within a specific light-year radius of a system. Multiple systems can be added for a wider spread."""
        def make_options(search_str):
            __options = discord_options.mapper_index(self.cfeed.discord_client, message_object)
            __options.set_main_header(
                "Select the base system you wish to add.\nNote: Additional base systems can be added or removed after feed creation by running the ‘!settings’ command.")
            db: Session = self.cfeed.service.get_session()

            def header_make(row_list:List[tb_systems],header_text):
                if len(row_list) > 0:
                    __options.add_header_row(header_text)
                    for i in row_list:
                        __options.add_option(discord_options.option_returns_object(name=i.name, return_object=i))
            try:
                header_make(db.query(tb_systems).filter(tb_systems.name.ilike("%{}%".format(search_str))).all(),"Systems")
                __options.add_header_row("Additional Options")
                __options.add_option(discord_options.option_returns_object("Search again",return_object=None))
            except Exception as ex:
                print(ex)
                db.rollback()
            finally:
                db.close()
                return __options

        __search = discord_options.mapper_return_noOptions(self.cfeed.discord_client, message_object)
        __search.set_main_header("Enter the name of a new base system.")
        __search.set_footer_text("Enter a name. Note: partial names are accepted: ")
        __selected_option = None
        while __selected_option is None:
            __search_name = await __search()
            __found_results = await self.cfeed.discord_client.loop.run_in_executor(None,partial(make_options,__search_name))
            __selected_option:tb_systems = await __found_results()
        __ly_range = discord_options.mapper_return_noOptions_requiresInt(self.cfeed.discord_client, message_object)
        __ly_range.set_main_header("Enter the maximum light-year radius for the selected base system.\n\n"
                                   "Only killmails occurring within the light-year range of your base system will appear in this feed.")
        __ly_range.set_footer_text("Enter an integer:")
        __range = await __ly_range()
        function_call = partial(tb_channels.commit_list_entry,__selected_option,self.cfeed.channel_id,self.cfeed.service,maxly=__range)
        await self.cfeed.discord_client.loop.run_in_executor(None, function_call)
        await self.reload(message_object)

    async def InsightOption_remove(self, message_object: discord.Message):
        """Remove a base system - Remove a selected base system from the feed."""
        def remove_system(system_id):
            db:Session = self.cfeed.service.get_session()
            try:
                tb_Filter_systems.get_remove(channel_id=self.cfeed.channel_id,filter_id=system_id,service_module=self.cfeed.service)
                db.commit()
            except Exception as ex:
                print(ex)
                raise InsightExc.Db.DatabaseError
            finally:
                db.close()

        def make_options():
            db:Session = self.cfeed.service.get_session()
            __remove = discord_options.mapper_index_withAdditional(self.cfeed.discord_client, message_object)
            __remove.set_main_header("Select the system you wish to remove as a base.")
            try:
                __remove.add_header_row("Systems currently set as base systems for this feed")
                for i in db.query(tb_Filter_systems).filter(tb_Filter_systems.channel_id==self.cfeed.channel_id).all():
                    __representation = "System: {}-----LY Range: {}".format(str(i.object_item.name),str(i.max))
                    __remove.add_option(discord_options.option_returns_object(name=__representation,return_object=i.filter_id))
            except:
                db.rollback()
            finally:
                db.close()
                return __remove
        __options = await self.cfeed.discord_client.loop.run_in_executor(None,make_options)
        system_id = await __options()
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(remove_system, system_id))
        await self.reload(message_object)

    async def InsightOptionRequired_supers(self,message_object:discord.Message):
        """Super tracking - Enable or disable tracking of supercarrier/titan targets within range of base systems."""
        __options = discord_options.mapper_return_yes_no(self.cfeed.discord_client, message_object)
        __options.set_main_header("Track supercarrier and titan activity in this channel?")
        __track_group_TF = await __options()
        if __track_group_TF:
            __mention_method = self.mention_options(message_object,"supercarrier/titan")
            __mention_enum = await __mention_method()
            await self.cfeed.discord_client.loop.run_in_executor(None, partial(self.modify_groups, self.super_ids,
                                                                               __mention_enum))
        else:
            await self.cfeed.discord_client.loop.run_in_executor(None, partial(self.modify_groups, self.super_ids,
                                                                               enum_mention.noMention, remove=True))
        await self.reload(message_object)

    async def InsightOptionRequired_capitals(self,message_object:discord.Message):
        """Capital tracking - Enable or disable tracking of capital (dread, carrier, FAX, Rorqual) targets within range of base systems."""
        __options = discord_options.mapper_return_yes_no(self.cfeed.discord_client, message_object)
        __options.set_main_header("Track capital (dread, carrier, FAX, Rorqual) activity in this channel?")
        __track_group_TF = await __options()
        if __track_group_TF:
            __mention_method = self.mention_options(message_object,"capital(dreads,carriers,FAX)")
            __mention_enum = await __mention_method()
            await self.cfeed.discord_client.loop.run_in_executor(None, partial(self.modify_groups, self.capital_ids,
                                                                               __mention_enum))
        else:
            await self.cfeed.discord_client.loop.run_in_executor(None, partial(self.modify_groups, self.capital_ids,
                                                                               enum_mention.noMention, remove=True))
        await self.reload(message_object)

    async def InsightOptionRequired_blops(self,message_object:discord.Message):
        """BLOPS tracking - Enable or disable tracking of black ops battleship targets within range of base systems."""
        __options = discord_options.mapper_return_yes_no(self.cfeed.discord_client, message_object)
        __options.set_main_header("Track black ops battleship activity in this channel?")
        __track_group_TF = await __options()
        if __track_group_TF:
            __mention_method = self.mention_options(message_object,"blackops battleships")
            __mention_enum = await __mention_method()
            await self.cfeed.discord_client.loop.run_in_executor(None, partial(self.modify_groups, self.blops_ids,
                                                                               __mention_enum))
        else:
            await self.cfeed.discord_client.loop.run_in_executor(None, partial(self.modify_groups, self.blops_ids,
                                                                               enum_mention.noMention, remove=True))
        await self.reload(message_object)

    async def InsightOptionRequired_maxage(self,message_object:discord.Message):
        """Set maximum killmail age - Sets the maximum delay, in minutes, that mails can be posted to the feed. Fetched mails occurring more than the set age will not be pushed to the channel."""
        def change_limit(new_limit):
            db: Session = self.cfeed.service.get_session()
            try:
                __row = tb_capRadar.get_row(self.cfeed.channel_id,self.cfeed.service)
                __row.max_km_age = new_limit
                db.merge(__row)
                db.commit()
            except Exception as ex:
                print(ex)
                raise InsightExc.Db.DatabaseError
            finally:
                db.close()

        __options = discord_options.mapper_return_noOptions_requiresInt(self.cfeed.discord_client, message_object)
        __options.set_main_header(
            "Enter the maximum delay, in minutes, that mails can be pushed to the channel. Mails occurring more than the set age will not be posted  to the channel.")
        __options.set_footer_text("Enter an integer:")
        _max_age = await __options()
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(change_limit, _max_age))
        await self.reload(message_object)

    async def InsightOption_sync(self, message_object: discord.Message):
        """Manage feed sync settings - Set up and manage EVE contact syncing to blacklist allies from appearing as targets in this radar feed."""
        await self.cfeed.command_sync(message_object)

from .. import capRadar
from discord_bot import discord_options
from database.db_tables import *