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

        def remove_row(token):
            db: Session = self.cfeed.service.get_session()
            try:
                row = db.query(tb_tokens).filter(tb_tokens.discord_user == self.cfeed.user_id,
                                                 tb_tokens.refresh_token == token).one()
                db.delete(row)
                db.commit()
            except Exception as ex:
                print(ex)
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
        try:
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
            await self.InsightOption_syncnow(message_object)
        except:
            await self.cfeed.discord_client.loop.run_in_executor(None, partial(remove_row, __resp.refresh_token))

    async def InsightOption_deleteToken(self, message_object: discord.Message):
        """Delete token - Deletes one of your added tokens and removes it from all channels that use it."""

        def delete_token(token):
            db: Session = self.cfeed.service.get_session()
            try:
                row = db.query(tb_tokens).filter(tb_tokens.discord_user == self.cfeed.user_id,
                                                 tb_tokens.refresh_token == token.refresh_token).one()
                db.delete(row)
                db.commit()
                return "ok"
            except Exception as ex:
                print(ex)
                return "An error occurred when deleting your token. Please delete the token from CCP's official website " \
                       "if you continue to get this error."
            finally:
                db.close()

        def get_options():
            _options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, message_object, timeout_seconds=75)
            _options.set_main_header(
                "These are all the tokens currently in the system. Select one to delete and remove it from all channels.")
            db: Session = self.cfeed.service.get_session()
            try:
                for token in db.query(tb_tokens).filter(tb_tokens.discord_user == self.cfeed.user_id).all():
                    _options.add_option(dOpt.option_returns_object(name=str(token), return_object=token))
                return _options
            except Exception as ex:
                print(ex)
                raise Exception("Error when getting your tokens")
            finally:
                db.close()

        _options = await self.cfeed.discord_client.loop.run_in_executor(None, get_options)
        rm_token = await _options()
        __code = await self.cfeed.discord_client.loop.run_in_executor(None, partial(delete_token, rm_token))
        await message_object.channel.send(str(__code))

    async def InsightOption_removeChannel(self, message_object: discord.Message):
        """Remove a token from Discord channel - Removes your token from a Discord channel"""
        pass

    async def InsightOption_syncnow(self, message_object: discord.Message):
        """Force sync - Forces an API pull on all of your tokens. Note: Insight automatically syncs your tokens every 8 hours."""
        await message_object.channel.send("Syncing your tokens now")
        await self.cfeed.discord_client.loop.run_in_executor(None,
                                                             partial(tb_tokens.sync_all_tokens, self.cfeed.user_id,
                                                                     self.cfeed.service))


from discord_bot import discord_options as dOpt
from database.db_tables import *
