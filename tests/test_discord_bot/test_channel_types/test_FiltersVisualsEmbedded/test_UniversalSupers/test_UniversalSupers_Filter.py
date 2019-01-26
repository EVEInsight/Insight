from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.UniverseSupers import UniverseSupers
from discord_bot.channel_types.FiltersVisualsEmbedded.visual_capradar import visual_capradar


class TestUniversalSupersFilter1(AbstractFilterTesting.AbstractFilterTesting):
    def need_api_download(self):
        return True

    def download_systems(self):
        return True

    @classmethod
    def populate_group_ids(cls):
        yield from [30, 659]

    @classmethod
    def assert_file_path(cls):
        return "UniversalSupers"

    @classmethod
    def filter_pass_assert_file(cls):
        yield "1_pass.txt"

    @classmethod
    def filter_fail_assert_file(cls):
        yield "1_fail.txt"

    @classmethod
    def filter_systems_ids(cls):
        yield 30000142

    @classmethod
    def InsightChannelType(cls):
        return UniverseSupers

    def mock_modify_before_view(self, filter_object: visual_capradar):
        filter_object.tracked_hostiles = filter_object.km.object_attackers
        filter_object.baseSystem = filter_object.km.object_system
        filter_object.list_typeGroup = filter_object.filters.object_filter_groups + filter_object.filters.object_filter_types
