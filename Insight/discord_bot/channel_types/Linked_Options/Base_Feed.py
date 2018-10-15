from . import options_base
import discord
from discord_bot import discord_options as dOpt
from database.db_tables import id_resolver
from functools import partial
from sqlalchemy.orm import *
from sqlalchemy import *
from typing import List
import InsightExc


class base_activefeed(options_base.Options_Base):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, nofeed_text.discord_text_nofeed_exist)
        super().__init__(insight_channel)

    # InsightOption_ InsightOptionRequired_
    def yield_options(self):
        yield from super().yield_options()
        yield (self.InsightOption_setMention, False)
        yield (self.InsightOption_setMentionEvery, False)
        yield (self.InsightOptionRequired_setAppearance, True)
        yield (self.InsightOption_start, False)
        yield (self.InsightOption_pause, False)
        yield (self.InsightOption_remove_opt, False)

    async def InsightOption_remove_opt(self,message_object:discord.Message):
        """Delete Feed  - Removes the currently active feed from this channel, deleting its configuration."""
        await self.cfeed.command_remove(message_object)

    async def InsightOption_pause(self,message_object:discord.Message):
        """Pause Feed  - Pauses the feed if it's currently running."""
        await self.cfeed.command_stop(message_object)

    async def InsightOption_start(self,message_object:discord.Message):
        """Start feed  - Starts the feed if it's currently paused."""
        await self.cfeed.command_start(message_object)

    async def InsightOptionRequired_setAppearance(self, message_object: discord.Message):
        """Change visual appearance - Set the visual appearance of rich embeds."""

        def set_appearance(app_id):
            db: Session = self.cfeed.service.get_session()
            try:
                __row: tb_channels = db.query(tb_channels).filter(tb_channels.channel_id == self.cfeed.channel_id).one()
                __row.appearance_id = app_id
                db.merge(__row)
                db.commit()
            except Exception as ex:
                print(ex)
                raise InsightExc.Db.DatabaseError
            finally:
                db.close()

        _options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, message_object)
        _options.set_main_header("Select a rich embed appearance. Appearances allow you to select a template for "
                                 "killmail presentation and differ in verbosity, size, and the amount of information "
                                 "provided. See https://github.com/Nathan-LS/Insight/wiki/Rich-Embed-Appearance for "
                                 "sample previews of each appearance. Note: appearances can be changed after feed "
                                 "creation by running the '!settings' command.")
        for ap in self.cfeed.linked_visual_base().appearance_options():
            _options.add_option(dOpt.option_returns_object(name=ap.get_desc(), return_object=ap.appearance_id()))
        a_id = await _options()
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(set_appearance, a_id))
        await self.reload(message_object)

    async def InsightOption_setMention(self, message_object: discord.Message):
        """Set global mention - NULL"""
        options = dOpt.mapper_index(self.cfeed.discord_client, message_object)
        options.set_main_header("Select mention mode.")
        options.add_option(dOpt.option_returns_object("No mention", return_object=enum_mention.noMention))
        options.add_option(dOpt.option_returns_object("@ here", return_object=enum_mention.here))
        options.add_option(dOpt.option_returns_object("@ everyone", return_object=enum_mention.everyone))
        row = await self.get_cached_copy()
        row.mention = await options()
        await self.save_row(row)
        await self.reload(message_object)

    async def InsightOption_setMentionEvery(self, message_object: discord.Message):
        """Set mention rate - NULL"""
        options = dOpt.mapper_return_noOptions_requiresFloat(self.cfeed.discord_client, message_object)
        options.set_main_header("Mention every: ")
        options.set_bit_length(5)
        row = await self.get_cached_copy()
        row.mention_every = await options()
        await self.save_row(row)
        await self.reload(message_object)


from database.db_tables import *
from .. import nofeed_text