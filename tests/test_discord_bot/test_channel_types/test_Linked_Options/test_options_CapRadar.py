from discord_bot.channel_types.capRadar import capRadar
from database.db_tables.filters import tb_Filter_systems, tb_Filter_groups, tb_Filter_types
import InsightExc
from tests.test_discord_bot.test_channel_types.test_Linked_Options import test_options_BaseFeed
from database.db_tables.filters.base_filter import mention_method
from functools import partial
import unittest


class TestOptions_CapRadarAddRemove(test_options_BaseFeed.TestOptions_BaseFeed):
    """tests with system names preloaded for use in search"""
    def setUp(self):
        super().setUp()
        self.import_systems(self.engine, full_data=True)

    @classmethod
    def feed_type(cls):
        return capRadar

    @unittest.SkipTest
    def test_InsightOption_lock_unlock(self): ...

    @unittest.SkipTest
    def test_InsightOption_remove_opt(self): ...

    @unittest.SkipTest
    def test_InsightOption_setMention(self): ...

    @unittest.SkipTest
    def test_InsightOption_setMentionEvery(self): ...

    @unittest.SkipTest
    def test_InsightOption_start_pause(self): ...

    @unittest.SkipTest
    def test_InsightOptionRequired_setAppearance(self): ...

    def test_InsightOptionRequired_add_remove(self):
        with self.subTest("Add"):
            self.reply("15W-GC")
            self.reply("0")
            self.reply("15")
            self.helper_future_run_call(self.options.InsightOptionRequired_add(self.message))
            s = tb_Filter_systems(30000861, 1)
            s.max = 15
            self.assertFilterContains(s, self.cached_row.object_filter_systems)
        with self.subTest("Modify existing range"):
            self.reply("15W-GC")
            self.reply("0")
            self.reply("10")
            self.helper_future_run_call(self.options.InsightOptionRequired_add(self.message))
            s = tb_Filter_systems(30000861, 1)
            s.max = 10
            self.assertFilterContains(s, self.cached_row.object_filter_systems)
        with self.subTest("Remove existing"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_remove(self.message))
            self.assertEqual(0, len(self.cached_row.object_filter_systems))


class TestOptions_CapRadarTrackCustom(TestOptions_CapRadarAddRemove):
    def setUp(self):
        super(TestOptions_CapRadarAddRemove, self).setUp()
        self.import_groups(self.engine, full_data=True)
        self.import_types(self.engine, full_data=True)

    @unittest.SkipTest
    def test_InsightOptionRequired_add_remove(self): ...

    def test_InsightOption_add_remove_custom(self):
        with self.subTest("Add type Revenant track"):
            self.reply("Revenant")
            self.reply("0")
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_addcustom(self.message))
            self.assertFilterContains(tb_Filter_types(3514, 1), self.cached_row.object_filter_types)
        with self.subTest("Change mention mode"):
            self.reply("3514")  # search by id
            self.reply("0")
            self.reply("1")
            self.helper_future_run_call(self.options.InsightOption_addcustom(self.message))
            t = tb_Filter_types(3514, 1)
            t.mention = mention_method.here
            self.assertFilterContains(t, self.cached_row.object_filter_types)
        with self.subTest("Add group track for Asteroid Sansha's Nation Dreadnought"):
            self.reply("Asteroid Sansha's Nation Dreadnought")
            self.reply("0")
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_addcustom(self.message))
            self.assertFilterContains(tb_Filter_groups(1687, 1), self.cached_row.object_filter_groups)
        with self.subTest("Change mention mode"):
            self.reply("1687")  # search by id
            self.reply("12")
            self.reply("1")
            self.helper_future_run_call(self.options.InsightOption_addcustom(self.message))
            t = tb_Filter_groups(1687, 1)
            t.mention = mention_method.here
            self.assertFilterContains(t, self.cached_row.object_filter_groups)
        self.assertEqual(2, len(self.cached_row.object_filter_types + self.cached_row.object_filter_groups))
        with self.subTest("Remove type"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_removecustom(self.message))
            self.assertEqual(0, len(self.cached_row.object_filter_types))
            self.assertEqual(1, len(self.cached_row.object_filter_groups))
        with self.subTest("Remove group"):
            self.reply("0")
            self.helper_future_run_call(self.options.InsightOption_removecustom(self.message))
            self.assertEqual(0, len(self.cached_row.object_filter_types))
            self.assertEqual(0, len(self.cached_row.object_filter_groups))


class TestOptions_CapRadar(test_options_BaseFeed.TestOptions_BaseFeed):
    @classmethod
    def feed_type(cls):
        return capRadar

    def helper_type_group_add_remove(self, track_items, coro_call):
        with self.subTest("Remove non existing"):
            self.reply("0")
            self.helper_future_run_call(coro_call())
            self.assertEqual(0, len(self.cached_row.object_filter_groups))
        with self.subTest("Add with @here"):
            self.reply("1")
            self.reply("1")
            self.helper_future_run_call(coro_call())
            for t in track_items:
                t.mention = mention_method.here
                self.assertFilterContains(t, self.cached_row.object_filter_types + self.cached_row.object_filter_groups)
                self.assertEqual(len(track_items),
                                 len(self.cached_row.object_filter_types + self.cached_row.object_filter_groups))
        with self.subTest("Modify mention to no mention"):
            self.reply("1")
            self.reply("0")
            self.helper_future_run_call(coro_call())
            for t in track_items:
                t.mention = mention_method.noMention
                self.assertFilterContains(t, self.cached_row.object_filter_types + self.cached_row.object_filter_groups)
                self.assertEqual(len(track_items),
                                 len(self.cached_row.object_filter_types + self.cached_row.object_filter_groups))
        with self.subTest("Remove"):
            self.reply("0")
            self.helper_future_run_call(coro_call())
            self.assertEqual(0, len(self.cached_row.object_filter_types + self.cached_row.object_filter_groups))

    def test_InsightOptionRequired_supers(self):
        self.helper_type_group_add_remove([tb_Filter_groups(i, 1) for i in [30, 659]],
                                          partial(self.options.InsightOptionRequired_supers, self.message))

    def test_InsightOptionRequired_capitals(self):
        self.helper_type_group_add_remove([tb_Filter_groups(i, 1) for i in [547, 485, 1538, 883]],
                                          partial(self.options.InsightOptionRequired_capitals, self.message))

    def test_InsightOptionRequired_blops(self):
        self.helper_type_group_add_remove([tb_Filter_groups(i, 1) for i in [898]],
                                          partial(self.options.InsightOptionRequired_blops, self.message))

    def test_InsightOptionRequired_atships(self):
        self.helper_type_group_add_remove([tb_Filter_groups(i, 1) for i in list(self.options.at_ship_ids())],
                                          partial(self.options.InsightOptionRequired_atships, self.message))

    def test_InsightOptionRequired_npc_officers(self):
        self.helper_type_group_add_remove([tb_Filter_groups(i, 1) for i in list(self.options.npc_officer_ids())],
                                          partial(self.options.InsightOptionRequired_npc_officers, self.message))

    def test_InsightOptionRequired_maxage(self):
        self.reply("5")
        self.helper_future_run_call(self.options.InsightOptionRequired_maxage(self.message))
        self.assertEqual(5, self.cached_row_specific.max_km_age)
        self.reply("10")
        self.helper_future_run_call(self.options.InsightOptionRequired_maxage(self.message))
        self.assertEqual(10, self.cached_row_specific.max_km_age)

    def test_InsightOption_sync(self):
        with self.assertRaises(InsightExc.userInput.Cancel):
            self.reply("4")  # cancel
            self.helper_future_run_call(self.options.InsightOption_sync(self.message))


