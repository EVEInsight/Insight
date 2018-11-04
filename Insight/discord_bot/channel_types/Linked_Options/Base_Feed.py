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
        yield (self.InsightOption_lockfeed, False)
        yield (self.InsightOption_unlockfeed, False)

    async def InsightOption_remove_opt(self,message_object:discord.Message):
        """Delete Feed - Removes and deletes the currently active feed in this channel."""
        await self.cfeed.command_remove(message_object)

    async def InsightOption_pause(self,message_object:discord.Message):
        """Pause Feed - Pauses the feed."""
        await self.cfeed.command_stop(message_object)

    async def InsightOption_start(self,message_object:discord.Message):
        """Start feed - Starts the feed."""
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
        """Set overall mention mode - Select the mention mode for any killmail posted to this feed."""
        options = dOpt.mapper_index(self.cfeed.discord_client, message_object)
        options.set_main_header("Select the mention mode for this feed. Any killmail posted to this feed can optionally "
                                "mention Discord channel users.")
        options.add_option(dOpt.option_returns_object("No mention", return_object=enum_mention.noMention))
        options.add_option(dOpt.option_returns_object("@ here", return_object=enum_mention.here))
        options.add_option(dOpt.option_returns_object("@ everyone", return_object=enum_mention.everyone))
        row = await self.get_cached_copy()
        row.mention = await options()
        await self.save_row(row)
        await self.reload(message_object)

    async def InsightOption_setMentionEvery(self, message_object: discord.Message):
        """Set mention rate - Set the delay between mentions."""
        options = dOpt.mapper_return_noOptions_requiresFloat(self.cfeed.discord_client, message_object)
        options.set_main_header("Select the limit between mentions in minutes. If the limit is exceeded, killmails will "
                                "be posted without mentions. Set this to '0' to have no limit where every killmail "
                                "will mention according to your set mention mode. Example: Setting this to '1' will "
                                "mention at most every 1 minute.")
        options.set_bit_length(5)
        row = await self.get_cached_copy()
        row.mention_every = await options()
        await self.save_row(row)
        await self.reload(message_object)

    async def InsightOption_lockfeed(self, message_object: discord.Message):
        """Lock feed - Lock a feed service from being modified by users without certain Discord channel roles."""
        self.cfeed.check_permission(message_object.author, required_level=1, ignore_channel_setting=True)
        if self.cfeed.cached_feed_table.modification_lock:
            raise InsightExc.DiscordError.NonFatalExit('This channel feed is already locked from unauthorized modifications.')
        options = dOpt.mapper_return_yes_no(self.cfeed.discord_client, message_object)
        options.set_main_header("Lock this feed from unauthorized access? Locking a feed prevents users lacking Discord channel "
                                "permissions from accessing or modifying feed settings. A locked feed can only be unlocked, modified, "
                                "or removed by a Discord channel user with at least one of the following "
                                "permissions:\n\nAdministrator\nManage Roles\nManage Messages\nManage Guild\n"
                                "Manage Channel\nManage webhooks\n\n")
        resp = await options()
        if resp:
            row = await self.get_cached_copy()
            row.modification_lock = True
            await self.save_row(row)
        await self.reload(message_object)

    async def InsightOption_unlockfeed(self, message_object: discord.Message):
        """Unlock feed - Unlock a previously locked feed service to allow any Discord channel user to modify settings."""
        self.cfeed.check_permission(message_object.author, required_level=1, ignore_channel_setting=True)
        if not self.cfeed.cached_feed_table.modification_lock:
            raise InsightExc.DiscordError.NonFatalExit("This channel feed is already unlocked. You can lock this"
                                                       " feed from unauthorized modifications with "
                                                       "the '!lock' command.")
        options = dOpt.mapper_return_yes_no(self.cfeed.discord_client, message_object)
        options.set_main_header("Unlock this channel feed? Unlocking a channel feed allows anyone in the channel to "
                                "modify feed behavior and settings.")
        resp = await options()
        if resp:
            row = await self.get_cached_copy()
            row.modification_lock = False
            await self.save_row(row)
        await self.reload(message_object)


from database.db_tables import *
from .. import nofeed_text