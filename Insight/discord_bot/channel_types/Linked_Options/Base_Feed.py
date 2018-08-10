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
        _options.set_main_header("Select a rich embed appearance.")
        for ap in self.cfeed.linked_visual_base().appearance_options():
            _options.add_option(dOpt.option_returns_object(name=ap.get_desc(), return_object=ap.appearance_id()))
        a_id = await _options()
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(set_appearance, a_id))
        await self.reload(message_object)


from database.db_tables import *
from .. import nofeed_text