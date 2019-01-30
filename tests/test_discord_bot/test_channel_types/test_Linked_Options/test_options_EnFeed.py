from tests.abstract.TestCases.AbstractBotReplyTesting import AbstractBotReplyTesting
from discord_bot.channel_types.enFeed import enFeed
from tests.mocks.libDiscord.TextChannel import TextChannel
from database.db_tables.discord import tb_enfeed, tb_channels, enum_kmType
from database.db_tables.filters import tb_Filter_groups, tb_Filter_alliances, tb_Filter_corporations, tb_Filter_characters
from discord_bot.channel_types.Linked_Options import opt_enfeed
from tests.mocks.libDiscord.Message import Message
from tests.mocks.libDiscord.User import User
import InsightExc
from database.db_tables.filters.base_filter import mention_method


class TestOptions_EnFeed(AbstractBotReplyTesting):
    def setUp(self):
        super().setUp()
        self.db.add(self.get_config_row().get_row(1, self.service))
        self.db.commit()
        text_channel = TextChannel(1, 1)
        self.feed = self.feed_type()(text_channel, self.service)
        self.options: opt_enfeed = self.feed.linked_options
        self.message = Message(text_channel, User(1, "Tester"), "Initiation message.")

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

    def test_InsightOptionRequired_add(self):
        with self.subTest("Add tracking for NC"):
            self.reply("Northern Coalition.")
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOptionRequired_add(self.message))
            self.assertFilterContains(tb_Filter_alliances(1727758877, 1), self.cached_row.object_filter_alliances)
        with self.subTest("Add tracking for Burn EDEN"):
            self.reply("BURN EDEN")
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOptionRequired_add(self.message))
            self.assertFilterContains(tb_Filter_corporations(761955047, 1), self.cached_row.object_filter_corporations)
        with self.subTest("Add tracking for Natuli"):
            self.reply("Natuli")
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOptionRequired_add(self.message))
            self.assertFilterContains(tb_Filter_characters(1326083433, 1), self.cached_row.object_filter_characters)

    def test_InsightOption_remove(self):
        with self.subTest("Cancel"):
            with self.assertRaises(InsightExc.userInput.Cancel):
                self.reply("0")
                self.helper_future_run_call(self.options.InsightOption_remove(self.message))
        self.db.merge(tb_Filter_characters(1326083433, 1))
        self.db.merge(tb_Filter_corporations(761955047, 1))
        self.db.merge(tb_Filter_alliances(1727758877, 1))
        self.db.commit()
        self.helper_future_run_call(self.options.reload(None))
        with self.subTest("Remove NC. tracking"):
            self.reply("2")
            self.helper_future_run_call(self.options.InsightOption_remove(self.message))
            self.assertFilterNotContains(tb_Filter_alliances(1727758877, 1), self.cached_row.object_filter_alliances)
        with self.subTest("Remove UDIE tracking"):
            self.reply("1")
            self.helper_future_run_call(self.options.InsightOption_remove(self.message))
            self.assertFilterNotContains(tb_Filter_corporations(761955047, 1), self.cached_row.object_filter_alliances)
        with self.subTest("Remove Natuli tracking"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_remove(self.message))
            self.assertFilterNotContains(tb_Filter_characters(1326083433, 1), self.cached_row.object_filter_alliances)

    def test_InsightOptionRequired_tracktype(self):
        with self.subTest("Losses only"):
            self.reply("2")
            self.helper_future_run_call(self.options.InsightOptionRequired_tracktype(self.message))
            self.assertEqual(enum_kmType.losses_only, self.cached_row_specific.show_mode)
        with self.subTest("Kills only"):
            self.reply("1")
            self.helper_future_run_call(self.options.InsightOptionRequired_tracktype(self.message))
            self.assertEqual(enum_kmType.kills_only, self.cached_row_specific.show_mode)
        with self.subTest("Both"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOptionRequired_tracktype(self.message))
            self.assertEqual(enum_kmType.show_both, self.cached_row_specific.show_mode)

    def test_InsightOptionRequired_trackpods(self):
        with self.subTest("Track pods"):
            self.reply("1")
            self.helper_future_run_call(self.options.InsightOptionRequired_trackpods(self.message))
            self.assertFilterNotContains(tb_Filter_groups(29, 1), self.cached_row.object_filter_groups)
        with self.subTest("Ignore pods"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOptionRequired_trackpods(self.message))
            self.assertFilterContains(tb_Filter_groups(29, 1), self.cached_row.object_filter_groups)

    def test_InsightOption_minValue(self):
        with self.subTest("5b"):
            self.reply("5b")
            self.helper_future_run_call(self.options.InsightOption_minValue(self.message))
            self.assertEqual(5e9, self.cached_row_specific.minValue)
        with self.subTest("5m"):
            self.reply("5m")
            self.helper_future_run_call(self.options.InsightOption_minValue(self.message))
            self.assertEqual(5e6, self.cached_row_specific.minValue)
        with self.subTest("5k"):
            self.reply("5k")
            self.helper_future_run_call(self.options.InsightOption_minValue(self.message))
            self.assertEqual(5e3, self.cached_row_specific.minValue)
        with self.subTest("-5b"):
            self.reply("-5b")
            self.helper_future_run_call(self.options.InsightOption_minValue(self.message))
            self.assertEqual(5e9, self.cached_row_specific.minValue)

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
