from discord_bot.channel_types.ProximityWatch import ProximityWatch
from database.db_tables.filters import tb_Filter_systems, tb_Filter_constellations, tb_Filter_regions
from tests.test_discord_bot.test_channel_types.test_Linked_Options import test_options_BaseFeed


class TestOptions_ProximityWatch(test_options_BaseFeed.TestOptions_BaseFeed):
    def setUp(self):
        super().setUp()
        self.import_system_constellation_region(self.engine, full_data=True)

    @classmethod
    def feed_type(cls):
        return ProximityWatch

    def test_InsightOptionRequired_addRegSys(self):
        with self.subTest("Add system GE-8JV"):
            self.reply("gE-8")
            self.reply("0")
            self.reply("10")
            self.helper_future_run_call(self.options.InsightOptionRequired_addRegSys(self.message))
            s = tb_Filter_systems(30001198, 1)
            s.max = 10
            self.assertFilterContains(s, self.cached_row.object_filter_systems)
        with self.subTest("Modify jump range for existing system"):
            self.reply("gE-8")
            self.reply("0")
            self.reply("20")
            self.helper_future_run_call(self.options.InsightOptionRequired_addRegSys(self.message))
            s = tb_Filter_systems(30001198, 1)
            s.max = 20
            self.assertFilterContains(s, self.cached_row.object_filter_systems)
        with self.subTest("Add constellation 9HXQ-G"):
            self.reply("9h")
            self.reply("2")
            self.helper_future_run_call(self.options.InsightOptionRequired_addRegSys(self.message))
            self.assertFilterContains(tb_Filter_constellations(20000175, 1), self.cached_row.object_filter_constellations)
        with self.subTest("Add region Catch"):
            self.reply("ca")
            self.reply("26")
            self.helper_future_run_call(self.options.InsightOptionRequired_addRegSys(self.message))
            self.assertFilterContains(tb_Filter_regions(10000014, 1), self.cached_row.object_filter_regions)
        self.assertEqual(3, len(self.cached_row.object_filter_regions + self.cached_row.object_filter_constellations
                                + self.cached_row.object_filter_systems))
        with self.subTest("Remove region"):
            self.reply("2")
            self.helper_future_run_call(self.options.InsightOption_rmRegSys(self.message))
            self.assertEqual(0, len(self.cached_row.object_filter_regions))
        with self.subTest("Remove constellation"):
            self.reply("1")
            self.helper_future_run_call(self.options.InsightOption_rmRegSys(self.message))
            self.assertEqual(0, len(self.cached_row.object_filter_constellations))
        with self.subTest("Remove system"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_rmRegSys(self.message))
            self.assertEqual(0, len(self.cached_row.object_filter_systems))
