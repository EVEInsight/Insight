from service.channel_manager import Channel_manager
from database.db_tables.eve import tb_kills
from tests.mocks import DiscordInsightClient


class ChannelManager(Channel_manager):
    def __init__(self, service):
        self.service = service
        self.client = None
        self.mock_mails_sent = []
        self.mock_messages_sent = []

    def get_discord_client(self):
        return DiscordInsightClient.DiscordInsightClient()

    def sy_get_all_channels(self):  # mock replacement
        yield 1

    def post_message(self,message_txt):
        for feed in self.sy_get_all_channels():
            try:
                self.mock_messages_sent.append(message_txt)
            except Exception as ex:
                print(ex)

    def send_km(self, km):
        assert isinstance(km, tb_kills)
        for feed in self.sy_get_all_channels():
            try:
                self.mock_mails_sent.append(km)  # mock send replacement feed.add_km(km)
            except Exception as ex:
                print(ex)
