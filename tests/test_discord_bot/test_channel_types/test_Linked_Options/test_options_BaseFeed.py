from tests.abstract.TestCases.AbstractBotReplyTesting import AbstractBotReplyTesting
from tests.mocks.libDiscord.TextChannel import TextChannel
from database.db_tables.discord import tb_enfeed, tb_channels
from discord_bot.channel_types.Linked_Options import opt_enfeed
from tests.mocks.libDiscord.Message import Message
from tests.mocks.libDiscord.User import User
from discord_bot.channel_types.enFeed import enFeed
from database.db_tables.filters.base_filter import mention_method
import InsightExc


class TestOptions_BaseFeed(AbstractBotReplyTesting):
    def setUp(self):
        super().setUp()
        self.db.add(self.get_config_row().get_row(1, self.service))
        self.db.commit()
        text_channel = TextChannel(1, 1)
        self.feed = self.feed_type()(text_channel, self.service)
        self.options: opt_enfeed = self.feed.linked_options
        self.message = Message(text_channel, User(1, "Tester", True), "Initiation message.")
        self.helper_future_run_call(self.service.channel_manager.add_feed_object(self.feed))

    @classmethod
    def get_config_row(cls):
        return cls.feed_type().linked_table()

    @classmethod
    def feed_type(cls):
        return enFeed

    @property
    def cached_row(self)->tb_channels:
        return self.feed.cached_feed_table

    @property
    def cached_row_specific(self)->tb_enfeed:
        return self.feed.cached_feed_specific

    def test_InsightOption_remove_opt(self):
        self.assertNotEqual(None, self.db.query(self.get_config_row()).filter(self.get_config_row().channel_id == 1).one_or_none())
        self.assertEqual(1, len(self.service.channel_manager._channel_feed_container))
        self.reply("1")
        self.helper_future_run_call(self.options.InsightOption_remove_opt(self.message))
        self.assertEqual(0, len(self.service.channel_manager._channel_feed_container))
        self.assertEqual(None, self.db.query(self.get_config_row()).filter(self.get_config_row().channel_id == 1).one_or_none())

    def test_InsightOption_setMention(self):
        with self.subTest("No mention"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_setMention(self.message))
            self.assertEqual(mention_method.noMention, self.cached_row.mention)
        with self.subTest("Here"):
            self.reply("1")
            self.helper_future_run_call(self.options.InsightOption_setMention(self.message))
            self.assertEqual(mention_method.here, self.cached_row.mention)
        with self.subTest("Everyone"):
            self.reply("2")
            self.helper_future_run_call(self.options.InsightOption_setMention(self.message))
            self.assertEqual(mention_method.everyone, self.cached_row.mention)

    def test_InsightOption_setMentionEvery(self):
        with self.subTest("5"):
            self.reply("5")
            self.helper_future_run_call(self.options.InsightOption_setMentionEvery(self.message))
            self.assertEqual(5, self.cached_row.mention_every)
        with self.subTest("10.2"):
            self.reply("10.2")
            self.helper_future_run_call(self.options.InsightOption_setMentionEvery(self.message))
            self.assertEqual(10.2, self.cached_row.mention_every)

    def test_InsightOption_start_pause(self):
        with self.subTest("Start"):
            self.helper_future_run_call(self.options.InsightOption_start(self.message))
            self.assertTrue(self.cached_row.feed_running)
        with self.subTest("Pause"):
            self.helper_future_run_call(self.options.InsightOption_pause(self.message))
            self.assertFalse(self.cached_row.feed_running)

    def test_InsightOption_lock_unlock(self):
        self.assertFalse(self.cached_row.modification_lock)
        with self.subTest("Lock"):
            self.reply("1")
            self.helper_future_run_call(self.options.InsightOption_lockfeed(self.message))
            self.assertTrue(self.cached_row.modification_lock)
            with self.assertRaises(InsightExc.DiscordError.NonFatalExit):
                self.reply("1")
                self.helper_future_run_call(self.options.InsightOption_lockfeed(self.message))
        with self.subTest("Unlock"):
            self.reply("1")
            self.helper_future_run_call(self.options.InsightOption_unlockfeed(self.message))
            self.assertFalse(self.cached_row.modification_lock)
            with self.assertRaises(InsightExc.DiscordError.NonFatalExit):
                self.reply("1")
                self.helper_future_run_call(self.options.InsightOption_unlockfeed(self.message))

    def test_InsightOptionRequired_setAppearance(self):
        self.assertEqual(0, self.cached_row.appearance_id)
        self.reply("2")
        self.helper_future_run_call(self.options.InsightOptionRequired_setAppearance(self.message))
        self.assertNotEqual(0, self.cached_row.appearance_id)

