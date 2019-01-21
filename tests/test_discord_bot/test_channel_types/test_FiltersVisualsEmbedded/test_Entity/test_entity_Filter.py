from tests.abstract.TestCases import AbstractFilterTesting
from database.db_tables.discord import enum_kmType
from discord_bot.channel_types.enFeed import enFeed


class TestEntityFilterKillsOnly1(AbstractFilterTesting.AbstractFilterTesting):
    """Test case for entity feed configured with tracked pilot, corp, and alliances. Set to show kills only"""
    def assert_file_path(self):
        return "EntityFeed"

    def get_config_row(self):
        row = super().get_config_row()
        row.show_mode = enum_kmType.kills_only
        return row

    def filter_pass_assert_file(self):
        yield "1_pass.txt"

    def filter_fail_assert_file(self):
        yield "1_fail.txt"

    def filter_character_ids(self):
        yield 317012339

    def filter_corporation_ids(self):
        yield 1431056470

    def filter_alliance_ids(self):
        yield 1727758877
        yield 498125261

    @property
    def InsightChannelType(self):
        return enFeed


class TestEntityFilterLossOnly2(TestEntityFilterKillsOnly1):
    """Test case for entity feed configured with tracked pilot, corp, and alliances. Set to show kills only"""

    def get_config_row(self):
        row = super().get_config_row()
        row.show_mode = enum_kmType.losses_only
        return row

    def filter_pass_assert_file(self):
        yield "2_pass.txt"

    def filter_fail_assert_file(self):
        yield "2_fail.txt"


class TestEntityFilterBoth3(TestEntityFilterKillsOnly1):
    """Test case for entity feed configured with tracked pilot, corp, and alliances. Set to show kills only"""

    def get_config_row(self):
        row = super().get_config_row()
        row.show_mode = enum_kmType.show_both
        return row

    def filter_pass_assert_file(self):
        yield "1_pass.txt"
        yield "2_pass.txt"

    def filter_fail_assert_file(self):
        yield "3_fail.txt"
