import asyncio

from . import options_base
from .. import direct_message
import discord
from functools import partial
from sqlalchemy.orm import Session
import InsightExc
from InsightUtilities import LimitManager


class Options_DM(options_base.Options_Base):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, direct_message.direct_message)
        super().__init__(insight_channel)

    def yield_options(self):
        yield (self.InsightOption_addToken, False)
        yield (self.InsightOption_deleteToken, False)
        yield (self.InsightOption_removeChannel, False)
        yield (self.InsightOption_syncnow, False)
        yield (self.InsightOption_viewtokens, False)
        yield from super().yield_options()

    def printout_my_tokens(self):
        db: Session = self.cfeed.service.get_session()
        return_str = "My Tokens:\n\n"
        try:
            for t in db.query(tb_tokens).filter(tb_tokens.discord_user == self.cfeed.user_id).order_by(tb_tokens.token_id).all():
                return_str += t.str_wChcount() + '\n\n'
            return return_str
        except Exception as ex:
            print(ex)
            raise InsightExc.Db.DatabaseError
        finally:
            db.close()

    async def InsightOption_addToken(self, message_object: discord.Message):
        """Add new token - Add a new token for syncing contact information related to pilots, corporations, or alliances."""
        trackq = dOpt.mapper_return_yes_no(self.cfeed.discord_client, message_object)
        trackq.set_main_header("Would you like the sync token to include contacts from your character contacts?")
        track_pilot = await trackq()

        trackq = dOpt.mapper_return_yes_no(self.cfeed.discord_client, message_object)
        trackq.set_main_header("Would you like the sync token to include contacts from corporation contacts?")
        track_corp = await trackq()

        trackq = dOpt.mapper_return_yes_no(self.cfeed.discord_client, message_object)
        trackq.set_main_header("Would you like the sync token to include contacts from alliance (if applicable) contacts?")
        track_alliance = await trackq()

        callback_state = await self.cfeed.service.sso.generate_sso_state()
        sso_link = self.cfeed.service.sso.get_sso_login(callback_state, scope_pilot=track_pilot, scope_corp=track_corp,
                                                        scope_alliance=track_alliance)
        if self.cfeed.service.config.get("WEBSERVER_ENABLED"):
            msg_txt = "1. Open this link to sign in to EVE Single Sign On (SSO). \n{}\n\n" \
                      "2. After clicking 'Authorize' on the character you wish to connect to Insight you will be redirected to: \n{}\n\n" \
                      "3. On success, please check this conversation to verify the token was successfully added.\n\n" \
                      "For more information on Single Sign On (SSO) see this help article: \nhttps://support.eveonline.com/hc/en-us/articles/205381192-Single-Sign-On-SSO-\n" \
                      "To revoke third party app access, delete the application from: \nhttps://community.eveonline.com/support/third-party-applications/\n\n" \
                      "This link will expire in 2 minutes." \
                .format(sso_link, self.cfeed.service.sso.get_callback_url())
            await message_object.author.send(msg_txt)
            state_event: asyncio.Event = await self.cfeed.service.sso.get_state_event(callback_state)
            try:
                await asyncio.wait_for(state_event.wait(), timeout=120)
                auth_code = await self.cfeed.service.sso.get_state_code(callback_state)
            except asyncio.TimeoutError:
                await self.cfeed.service.sso.invalidate_state(callback_state)
                raise InsightExc.userInput.Cancel(message="The previous SSO login link is no longer valid as Insight "
                                                          "did not receive a callback. Please rerun this command again "
                                                          "to retry.")
        else:
            _options = dOpt.mapper_return_noOptions(self.cfeed.discord_client, message_object, timeout_seconds=400)
            msg_txt = "1. Open this link to sign in to EVE Single Sign On (SSO). \n{}\n\n" \
                      "2. After clicking 'Authorize' on the character you wish to connect to Insight you will be redirected to: \n{}\n\n" \
                      "3. Copy the content of your browser address bar into this conversation."\
                      "\nThe URL you paste should look similar to this:\n{}\n\n"\
                      "For more information on Single Sign On (SSO) see this help article https://support.eveonline.com/hc/en-us/articles/205381192-Single-Sign-On-SSO-\n" \
                      "To revoke third party app access, delete the application from https://community.eveonline.com/support/third-party-applications/"\
                .format(sso_link,self.cfeed.service.sso.get_callback_url(),
                        self.cfeed.service.sso.get_callback_example())
            _options.set_main_header(msg_txt)
            _options.set_footer_text("Please copy the URL into this conversation: ")
            response_auth_url = await _options()
            auth_code = self.cfeed.service.sso.clean_auth_code(response_auth_url)
        funct_call = partial(tb_tokens.generate_from_auth, self.cfeed.user_id, auth_code, self.cfeed.service)
        __resp = await self.cfeed.discord_client.loop.run_in_executor(None, funct_call)
        try:
            if not track_pilot:
                __resp.character_id = None
            if not track_corp:
                __resp.corporation_id = None
            if not track_alliance:
                __resp.alliance_id = None
            await self.save_row(__resp)
            await self.reload(message_object)
            await self.InsightOption_syncnow(message_object)
        except Exception as ex:
            await self.cfeed.discord_client.loop.run_in_executor(None,
                                                                 partial(self.cfeed.service.sso.delete_token, __resp))
            raise ex

    async def InsightOption_deleteToken(self, message_object: discord.Message):
        """Delete token - Delete one of your added tokens and remove it from all channels."""
        def get_options():
            _options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, message_object)
            _options.set_main_header(
                "These are all the tokens currently in the system. Selecting a token will delete and remove it from all channels.")
            db: Session = self.cfeed.service.get_session()
            try:
                for token in db.query(tb_tokens).filter(tb_tokens.discord_user == self.cfeed.user_id).order_by(tb_tokens.token_id).all():
                    _options.add_option(dOpt.option_returns_object(name=token.str_wChcount(), return_object=token))
                return _options
            except Exception as ex:
                print(ex)
                raise InsightExc.Db.DatabaseError
            finally:
                db.close()

        _options = await self.cfeed.discord_client.loop.run_in_executor(None, get_options)
        rm_token = await _options()
        await self.cfeed.discord_client.loop.run_in_executor(None,
                                                             partial(self.cfeed.service.sso.delete_token, rm_token))
        await self.reload(message_object)

    async def InsightOption_removeChannel(self, message_object: discord.Message):
        """Remove a token from Discord channel - Remove your token from a Discord channel."""
        def get_options():
            db: Session = self.cfeed.service.get_session()
            _options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, message_object)
            _options.set_main_header(
                "These are your tokens used by Discord channels. Select a channel to remove your token.")
            try:
                for t in db.query(tb_tokens).filter(tb_tokens.discord_user == self.cfeed.user_id).order_by(tb_tokens.token_id).all():
                    if len(t.object_channels) > 0:
                        _options.add_header_row('Token ID: {}'.format(t.token_id))
                        for channel in t.object_channels:
                            cinfo = str(channel.channel_id)
                            try:
                                ch = self.cfeed.discord_client.get_channel(channel.channel_id)
                                if ch is not None:
                                    cname = ch.name
                                    sname = ch.guild.name
                                    cinfo = "{}({})".format(str(cname), str(sname))
                            except Exception as ex:
                                print(ex)
                            _options.add_option(dOpt.option_returns_object(name=cinfo, return_object=channel))
            except Exception as ex:
                print(ex)
                raise InsightExc.Db.DatabaseError
            finally:
                db.close()
            return _options

        options = await self.cfeed.discord_client.loop.run_in_executor(None, get_options)
        row = await options()
        await self.delete_row(row)
        await self.reload(message_object)

    async def InsightOption_syncnow(self, message_object: discord.Message):
        """Force sync - Force an API pull on all of your tokens. Note: Insight automatically syncs your tokens every 9 hours by default."""
        async with (await LimitManager.cm_hp(message_object.channel)):
            await message_object.channel.send("Syncing your tokens now")
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(tb_tokens.sync_all_tokens,
                                                                           self.cfeed.user_id, self.cfeed.service))
        await self.InsightOption_viewtokens(message_object)

    async def InsightOption_viewtokens(self, message_object: discord.Message):
        """View my tokens - View information on all tokens you have with Insight."""
        resp = await self.cfeed.discord_client.loop.run_in_executor(None, self.printout_my_tokens)
        async with (await LimitManager.cm(message_object.channel)):
            await message_object.channel.send("{}\n{}".format(message_object.author.mention, resp))

    async def InsightOptionAbstract_addchannel(self):
        async with (await LimitManager.cm_hp(self.cfeed.channel_discord_object)):
            message_object = await self.cfeed.channel_discord_object.send(
                "This tool will assist in adding a token to a channel")
        message_object.author = self.cfeed.author

        def make_options():
            _options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, message_object)
            _options.set_main_header(
                "Select one of your tokens to add to the feed. If you do not have any tokens created yet, select the 'cancel' option"
                " and do the following:\n\nStep 1. Direct Message this bot with the command '!sync'.\n\nStep 2. Select the option"
                " to add a new token.\n\nStep 3. Follow the steps needed to add a token and then rerun the command '!sync' "
                "in the channel you wish to sync your contacts with.")
            db: Session = self.cfeed.service.get_session()
            try:
                _options.add_header_row("Your available tokens")
                for token in db.query(tb_tokens).filter(tb_tokens.discord_user == self.cfeed.user_id).order_by(tb_tokens.token_id).all():
                    _options.add_option(dOpt.option_returns_object(name=token.str_wChcount(), return_object=token))
                return _options
            except Exception as ex:
                print(ex)
                raise InsightExc.Db.DatabaseError
            finally:
                db.close()

        options = await self.cfeed.discord_client.loop.run_in_executor(None, partial(make_options))
        return await options()


from discord_bot import discord_options as dOpt
from database.db_tables import *
