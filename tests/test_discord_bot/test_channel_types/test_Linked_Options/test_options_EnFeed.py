from discord_bot.channel_types.enFeed import enFeed
from database.db_tables.discord import enum_kmType
from database.db_tables.filters import tb_Filter_groups, tb_Filter_alliances, tb_Filter_corporations, tb_Filter_characters, tb_Filter_types
import InsightExc
from tests.test_discord_bot.test_channel_types.test_Linked_Options import test_options_BaseFeed


class TestOptions_EnFeed(test_options_BaseFeed.TestOptions_BaseFeed):
    @classmethod
    def feed_type(cls):
        return enFeed

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
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_remove(self.message))
            self.assertFilterNotContains(tb_Filter_alliances(1727758877, 1), self.cached_row.object_filter_alliances)
        with self.subTest("Remove UDIE tracking"):
            self.reply("1")
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_remove(self.message))
            self.assertFilterNotContains(tb_Filter_corporations(761955047, 1), self.cached_row.object_filter_alliances)
        with self.subTest("Remove Natuli tracking"):
            self.reply("0")
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
        with self.subTest("Invalid input"):
            with self.assertRaises(InsightExc.userInput.NotFloat):
                self.reply("not a number")
                self.helper_future_run_call(self.options.InsightOption_minValue(self.message))
        with self.subTest("0"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_minValue(self.message))
            self.assertEqual(0.0, self.cached_row_specific.minValue)

    def test_InsightOption_maxValue(self):
        with self.subTest("5b"):
            self.reply("5b")
            self.helper_future_run_call(self.options.InsightOption_maxValue(self.message))
            self.assertEqual(5e9, self.cached_row_specific.maxValue)
        with self.subTest("5m"):
            self.reply("5m")
            self.helper_future_run_call(self.options.InsightOption_maxValue(self.message))
            self.assertEqual(5e6, self.cached_row_specific.maxValue)
        with self.subTest("Invalid input"):
            with self.assertRaises(InsightExc.userInput.NotFloat):
                self.reply("not a number")
                self.helper_future_run_call(self.options.InsightOption_maxValue(self.message))
        with self.subTest("Less than floor"):
            with self.assertRaises(InsightExc.InsightException):
                self.reply("5b") # set high min value
                self.helper_future_run_call(self.options.InsightOption_minValue(self.message))
                self.assertEqual(5e9, self.cached_row_specific.minValue)
                self.reply("5m")
                self.helper_future_run_call(self.options.InsightOption_maxValue(self.message))
        with self.subTest("0"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_maxValue(self.message))
            self.assertEqual(1e60, self.cached_row_specific.maxValue)

    def test_InsightOption_addRemoveShipBlackList(self):
        self.import_type_group_category(self.engine, full_data=True)  # temp before each. I am lazy and dont feel like making a new class right now
        with self.subTest("Add Drake"):
            self.reply("drake")
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_addShipBlackList(self.message))
            self.assertFilterContains(tb_Filter_types(24698, 1), self.cached_row.object_filter_types)
        with self.subTest("Add rorq"):
            self.reply("rorq")
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_addShipBlackList(self.message))
            self.assertFilterContains(tb_Filter_types(24698, 1), self.cached_row.object_filter_types)
            self.assertFilterContains(tb_Filter_types(28352, 1), self.cached_row.object_filter_types)
        with self.subTest("Remove Drake"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_removeShipBlackList(self.message))  # remove drake
            self.assertFilterContains(tb_Filter_types(28352, 1), self.cached_row.object_filter_types)  # still contain rorq
            self.assertFilterNotContains(tb_Filter_types(24698, 1), self.cached_row.object_filter_types)  # no drake
        with self.subTest("Remove Rorq"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_removeShipBlackList(self.message))  # remove rorq
            self.assertEqual(0, len(self.cached_row.object_filter_types))

