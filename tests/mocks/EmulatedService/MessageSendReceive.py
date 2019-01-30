import InsightUtilities
from tests.mocks.libDiscord import TextChannel, Message, User
import janus


class MessageSendReceive(metaclass=InsightUtilities.InsightSingleton):
    def __init__(self):
        self.message_buffer = []
        self.user_messages = janus.Queue()

    def send_message(self, msg):
        if isinstance(msg, str):
            msg_object = Message.Message(TextChannel.TextChannel(1, 1), User.User(1), msg)
        else:
            raise NotImplementedError
        self.message_buffer.append(msg_object)

    def respond_to_bot(self, msg):
        self.user_messages.sync_q.put_nowait(Message.Message(TextChannel.TextChannel(1, 1), User.User(1), msg))

    async def wait_for_message(self):
        return await self.user_messages.async_q.get()

    def pop_message(self):
        return self.message_buffer[-1]
