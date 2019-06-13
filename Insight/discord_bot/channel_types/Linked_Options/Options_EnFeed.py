from . import Base_Feed
import discord
from discord_bot import discord_options as dOpt
from database.db_tables import id_resolver
from functools import partial
from sqlalchemy.orm import *
from sqlalchemy import *
from typing import List
import InsightExc
from discord_bot.OptionLogic.EntityOptions import *


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
        yield (self.InsightOption_maxValue, False)
        yield (self.InsightOption_addShipBlackList, False)
        yield (self.InsightOption_removeShipBlackList, False)
        yield from super().yield_options()

    async def InsightOptionRequired_add(self, message_object:discord.Message):
        """Add a new tracked entity  - Add an entity (pilot, corp, or alliance) to track involved PvP activity. You can add more than 1 entity to a channel."""
        await AddEntityOption(self.cfeed, message_object).run()

    async def InsightOption_remove(self,message_object:discord.Message):
        """Remove a tracked entity - Remove tracking of PvP activity for a previously added pilot, corp, or alliance."""
        await RemoveEntityOption(self.cfeed, message_object).run()

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
        await MinValueOption(self.cfeed, message_object).run()

    async def InsightOption_maxValue(self, message_object: discord.Message):
        """Set maximum ISK value - Set the maximum ISK value for killmails."""
        await MaxValueOption(self.cfeed, message_object).run()

    async def InsightOption_addShipBlackList(self, message_object: discord.Message):
        """Add ship to blacklist - null"""
        await AddShipOption(self.cfeed, message_object).run()

    async def InsightOption_removeShipBlackList(self, message_object: discord.Message):
        """Remove a ship from blacklist - null"""
        await RemoveShipOption(self.cfeed, message_object).run()


from .. import enFeed
from database.db_tables import *