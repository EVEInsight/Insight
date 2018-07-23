from . import options_base
from .. import capRadar, direct_message
import discord
from functools import partial
from sqlalchemy.orm import Session
import asyncio
import InsightExc


class Options_Sync(options_base.Options_Base):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, capRadar.capRadar)
        super().__init__(insight_channel)

    async def InsightOption_addToken(self, message_object: discord.Message):
        """Add new token - Adds a new token for syncing contact information related to pilots, corporations, or alliances."""
        user_channel: direct_message.direct_message = await self.cfeed.channel_manager.get_user_dm(message_object)

        def write_token(token_row):
            db: Session = self.cfeed.service.get_session()
            try:
                __row = tb_discord_tokens(channel_id=self.cfeed.channel_id, token=token_row.refresh_token)
                db.merge(__row)
                db.commit()
                return "ok"
            except Exception as ex:
                print(ex)
                return "An error occurred attempting to enable this token for the channel."
            finally:
                db.close()

        if isinstance(user_channel, direct_message.direct_message):
            await message_object.channel.send(
                "{} I opened a direct message with you. Please read it.".format(message_object.author.mention))
            try:
                __token = await user_channel.linked_options.InsightOptionAbstract_addchannel()
                assert isinstance(__token, tb_tokens)
                __resp = await self.cfeed.discord_client.loop.run_in_executor(None, partial(write_token, __token))
                await message_object.channel.send(str(__resp))
                if __resp != "ok":
                    raise Exception("An error occurred when saving the token to channel")
                await self.InsightOption_syncnow(message_object)
            except Exception as ex:
                await message_object.channel.send("No changes were made to the token configuration for this channel")

    async def InsightOption_removeToken(self, message_object: discord.Message):
        """Remove token - Removes a token from the channel along with any synced contacts associated with it."""

        def remove_token(token_row):
            db: Session = self.cfeed.service.get_session()
            try:
                db.delete(token_row)
                db.commit()
                return "ok"
            except Exception as ex:
                print(ex)
                return "An error occurred when attempting to remove this token from the channel"
            finally:
                db.close()

        def get_options():
            _options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, message_object)
            _options.set_main_header(
                "Delete a token from this channel, removing all associated contacts in the blacklist.")
            db: Session = self.cfeed.service.get_session()
            try:
                for token in db.query(tb_discord_tokens).filter(
                        tb_discord_tokens.channel_id == self.cfeed.channel_id).all():
                    _options.add_option(dOpt.option_returns_object(name=str(token), return_object=token))
            except Exception as ex:
                print(ex)
            finally:
                db.close()
            return _options

        __options = await self.cfeed.discord_client.loop.run_in_executor(None, get_options)
        selected_row = await __options()
        _resp = await self.cfeed.discord_client.loop.run_in_executor(None, partial(remove_token, selected_row))
        await message_object.channel.send(_resp)
        if _resp == "ok":
            await self.InsightOption_syncnow(message_object)

    async def InsightOption_syncnow(self, message_object: discord.Message = None):
        """Force sync - Updates the channel's allies list if you have SSO tokens assigned to it."""

        def sync_contacts():
            db: Session = self.cfeed.service.get_session()
            try:
                __row = db.query(tb_channels).filter(tb_channels.channel_id == self.cfeed.channel_id).one()
                __row.sync_api_contacts(self.cfeed.service)
                db.commit()
                return __row.str_tokens()
            except Exception as ex:
                print(ex)
                return "Something went wrong when updating this channel's ignore lists with the tokens."
            finally:
                db.close()

        if message_object is not None:
            await self.cfeed.channel_discord_object.send("Syncing ignored ally capRadar contact lists now")
        __resp = await self.cfeed.discord_client.loop.run_in_executor(None, sync_contacts)
        await self.cfeed.channel_discord_object.send(__resp)
        await self.cfeed.async_load_table()


from discord_bot import discord_options as dOpt
from database.db_tables import *
