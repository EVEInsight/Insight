from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.UniverseSupers import UniverseSupers
from discord_bot.channel_types.FiltersVisualsEmbedded.visual_capradar import visual_capradar


class TestUniversalSupersFilter1(AbstractFilterTesting.AbstractFilterTesting):
    def need_api_download(self):
        return True

    def download_systems(self):
        return True

    def populate_group_ids(self):
        yield from [30, 659]

    def assert_file_path(self):
        return "UniversalSupers"

    def filter_pass_assert_file(self):
        yield "1_pass.txt"

    def filter_fail_assert_file(self):
        yield "1_fail.txt"

    def filter_systems_ids(self):
        yield 30000142

    @property
    def InsightChannelType(self):
        return UniverseSupers

    def mock_modify_before_view(self, filter_object: visual_capradar):
        filter_object.tracked_hostiles = filter_object.km.object_attackers
        filter_object.baseSystem = filter_object.km.object_system
        filter_object.list_typeGroup = filter_object.filters.object_filter_groups + filter_object.filters.object_filter_types
