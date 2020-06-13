from .UnboundCommandBase import *


class EightBall(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.responses = self.config.get("8BALL_RESPONSES")

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs)->str:
        return str(random.choice(self.responses))


