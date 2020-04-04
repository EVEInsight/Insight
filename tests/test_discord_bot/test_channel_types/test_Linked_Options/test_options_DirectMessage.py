from discord_bot.channel_types.direct_message import direct_message
from database.db_tables.filters import tb_Filter_systems, tb_Filter_constellations, tb_Filter_regions
from tests.test_discord_bot.test_channel_types.test_Linked_Options import test_options_BaseFeed
import InsightExc
from discord_bot.channel_types.Linked_Options.Options_DM import Options_DM
from tests.mocks.libDiscord import DMChannel, Message, User
from tests.abstract.TestCases import AbstractSSOTesting, AbstractBotReplyTesting
from database.db_tables.sso import tb_tokens
from unittest.mock import MagicMock, Mock
from service.EVEsso import EVEsso
from database.db_tables.discord import tb_discord_tokens, tb_channels
import InsightUtilities
import requests


class TestOptionsDirectMessage_AddNewToken(AbstractBotReplyTesting.AbstractBotReplyTesting, AbstractSSOTesting.AbstractSSOTesting):
    def setUp(self):
        AbstractSSOTesting.AbstractSSOTesting.setUp(self)
        AbstractBotReplyTesting.AbstractBotReplyTesting.setUp(self)
        t = tb_tokens(1, self.refresh_token)
        self.db.add(t)
        self.db.commit()
        self.db.refresh(t)
        self.sso.get_token(t)
        self.mock_replace = EVEsso.get_token_from_auth
        EVEsso.get_token_from_auth = MagicMock(return_value={"refresh_token": t.refresh_token, "access_token": t.token})
        channel = DMChannel.DMChannel(1)
        channel.recipient = User.User(1, "Tester", True)
        self.feed = direct_message(DMChannel.DMChannel(1), self.service)
        self.options: Options_DM = self.feed.linked_options
        self.message = Message.Message(channel, channel.recipient, "Initiation message.")
        self.service.sso = self.sso
        self.db.delete(t)
        self.db.commit()

    def tearDown(self):
        AbstractSSOTesting.AbstractSSOTesting.tearDown(self)
        AbstractBotReplyTesting.AbstractBotReplyTesting.tearDown(self)
        EVEsso.get_token_from_auth = self.mock_replace

    def test_InsightOption_addTokenValidCallBack(self):
        self.reply("https://github.eveinsight.net/Insight/callback?code=ExampleCallbackAuthCode")
        self.reply("1")
        self.reply("0")
        self.reply("1")
        self.helper_future_run_call(self.options.InsightOption_addToken(self.message))
        t = self.helper_get_row(1)
        self.assertEqual(self.assert_char_id, t.character_id)
        self.assertEqual(None, t.corporation_id)
        self.assertEqual(self.assert_alliance_id, t.alliance_id)
        self.assertLess(30, len(t.object_contacts_pilots))
        self.assertLess(10, len(t.object_contacts_corps))
        self.assertLess(10, len(t.object_contacts_alliances))


class TestOptionsDirectMessage_TokenOperations(AbstractBotReplyTesting.AbstractBotReplyTesting):
    def setUp(self):
        super().setUp()
        InsightUtilities.ColumnEncryption()._set_random_key()
        t1 = tb_tokens(1, "NULLTestingToken")
        self.db.add(t1)
        self.db.commit()
        self.db.refresh(t1)
        for i in range(10, 12):
            self.db.add(tb_channels(i))
            self.db.add(tb_discord_tokens(i, t1.token_id))
        self.db.commit()
        self.db.refresh(t1)
        self.mock_sso = EVEsso._get_config
        EVEsso._get_config = MagicMock(return_value=None)
        self.service.sso = EVEsso(self.service)
        self.mock_requests = requests.post
        requests.post = MagicMock(side_effect=InsightExc.databaseError.DatabaseError)
        channel = DMChannel.DMChannel(1)
        channel.recipient = User.User(1, "Tester", True)
        self.feed = direct_message(DMChannel.DMChannel(1), self.service)
        self.options: Options_DM = self.feed.linked_options
        self.message = Message.Message(channel, channel.recipient, "Initiation message.")

    def tearDown(self):
        super().tearDown()
        EVEsso._get_config = self.mock_sso
        requests.post = self.mock_requests

    def test_InsightOption_deleteToken(self):
        self.assertEqual(1, len(self.db.query(tb_tokens).all()))
        self.assertEqual(2, len(self.db.query(tb_discord_tokens).all()))
        with self.assertRaises(InsightExc.SSO.SSOerror):  # regardless of api call outcome to CCP to delete token the token is delete from database
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_deleteToken(self.message))
        self.assertEqual(0, len(self.db.query(tb_tokens).all()))
        self.assertEqual(0, len(self.db.query(tb_discord_tokens).all()))

    def test_InsightOption_removeChannel(self):
        with self.subTest("Remove 1 linked channel"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_removeChannel(self.message))
            self.assertTrue(10 not in [i.channel_id for i in self.db.query(tb_discord_tokens).all()])
            self.assertEqual(1, len(self.db.query(tb_tokens).all()))
            self.assertEqual(1, len(self.db.query(tb_discord_tokens).all()))
        with self.subTest("Remove last linked channel"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_removeChannel(self.message))
            self.assertEqual(1, len(self.db.query(tb_tokens).all()))
            self.assertEqual(0, len(self.db.query(tb_discord_tokens).all()))


