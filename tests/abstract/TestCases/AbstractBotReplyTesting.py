from tests.abstract import DatabaseTesting, AsyncTesting
from tests.abstract import AsyncTesting
from discord_bot.discord_options import mapper_index, option_returns_object, option_calls_coroutine
from tests.mocks import DiscordInsightClient
from tests.mocks.libDiscord.TextChannel import TextChannel
from tests.mocks.libDiscord.Message import Message
from tests.mocks.libDiscord.User import User
import asyncio
from tests.mocks.EmulatedService.MessageSendReceive import MessageSendReceive
import InsightUtilities
from database.db_tables.filters.base_filter import mention_method, listTypeEnum


class AbstractBotReplyTesting(DatabaseTesting.DatabaseTesting, AsyncTesting.AsyncTesting):
    def setUp(self):
        DatabaseTesting.DatabaseTesting.setUp(self)
        AsyncTesting.AsyncTesting.setUp(self)
        self.client = DiscordInsightClient.DiscordInsightClient()
        self.start_event_loop()
        self.messageEmulator = MessageSendReceive()

    def tearDown(self):
        DatabaseTesting.DatabaseTesting.tearDown(self)
        AsyncTesting.AsyncTesting.tearDown(self)
        InsightUtilities.InsightSingleton.clear_instance_references()

    def helper_future_run_call(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result(10)

    def reply(self, content):
        MessageSendReceive().respond_to_bot(str(content))

    def helper_filter_contains(self, filter_object, filter_row_list):
        if filter_object.mention == None:
            filter_object.mention = mention_method.noMention
        if filter_object.list_type == None:
            filter_object.list_type = listTypeEnum.nolist
        for i in filter_row_list:
            if i.channel_id == filter_object.channel_id and i.filter_id == filter_object.filter_id and i.list_type == \
                    filter_object.list_type and i.min == filter_object.min and i.max == filter_object.max \
                    and i.mention == filter_object.mention:
                return True
        return False

    def assertFilterContains(self, filter_object, filter_row_list):
        self.assertTrue(self.helper_filter_contains(filter_object,filter_row_list))

    def assertFilterNotContains(self, filter_object, filter_row_list):
        self.assertFalse(self.helper_filter_contains(filter_object,filter_row_list))
