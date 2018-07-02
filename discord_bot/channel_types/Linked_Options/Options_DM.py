from . import options_base
from .. import direct_message
import discord
from functools import partial
from sqlalchemy.orm import Session


class Options_DM(options_base.Options_Base):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, direct_message.direct_message)
        super().__init__(insight_channel)

    async def InsightOption_addToken(self, message_object: discord.Message):
        """Add new token - Adds a new token for syncing contact information related to pilots, corporations, or alliances."""

        async def track_this(row_object, type_str):
            if row_object is not None:
                track = dOpt.mapper_return_yes_no(self.cfeed.discord_client, message_object, timeout_seconds=60)
                track.set_main_header(
                    "Sync standings for {} {} for this token?".format(type_str, row_object.get_name()))
                return await track()
            return False

        def save_changes(row):
            db: Session = self.cfeed.service.get_session()
            try:
                db.merge(row)
                db.commit()
                return "ok"
            except Exception as ex:
                print(ex)
                return "An error occurred when saving the token to the database, please try again later."
            finally:
                db.close()

        _options = dOpt.mapper_return_noOptions(self.cfeed.discord_client, message_object, timeout_seconds=240)
        _options.set_main_header(
            "Open this link and login to EVE's SSO system. After clicking 'Authorize' and being redirected to a blank webpage, copy and paste the content of your browser's "
            "address bar into this conversation: \n{}"
            "\n\nThe URL you paste should look similar to this:\n{}"
            .format(self.cfeed.service.sso.get_sso_login(), self.cfeed.service.sso.get_callback_example()))
        _options.set_footer_text("Please copy and paste the URL in this conversation: ")
        auth_code = await _options()
        funct_call = partial(tb_tokens.generate_from_auth, self.cfeed.user_id, auth_code, self.cfeed.service)
        __resp = await self.cfeed.discord_client.loop.run_in_executor(None, funct_call)
        if not isinstance(__resp, tb_tokens):
            await message_object.channel.send(__resp)
            raise Exception("Error when generating token row")
        if not await track_this(__resp.object_pilot, "pilot"):
            __resp.character_id = None
        if not await track_this(__resp.object_corp, "corporation"):
            __resp.corporation_id = None
        if not await track_this(__resp.object_alliance, "alliance"):
            __resp.alliance_id = None
        __code = await self.cfeed.discord_client.loop.run_in_executor(None, partial(save_changes, __resp))
        await message_object.channel.send(str(__code))
        if __code != "ok":
            raise Exception("Error occurred when saving token tow")

    async def InsightOption_deleteToken(self, message_object: discord.Message):
        """Delete token - Deletes one of your added tokens and removes it from all channels that use it."""
        pass

    async def InsightOption_removeChannel(self, message_object: discord.Message):
        """Remove a token from Discord channel - Removes your token from a Discord channel"""
        pass

    async def InsightOption_syncnow(self, message_object: discord.Message):
        """Force sync - Forces an API pull on all of your tokens. Note: Insight automatically syncs your tokens every 8 hours."""
        pass


from discord_bot import discord_options as dOpt
from database.db_tables import *
