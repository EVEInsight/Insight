from .UnboundCommandBase import *
from InsightUtilities import MemTracker


class MemoryDiagnostic(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.cLock = asyncio.Lock(loop=self.client.loop)

    def command_description(self):
        return "Memory Diagnostic - Display the largest items in memory."

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs)->str:
        result = await self.client.loop.run_in_executor(None, MemTracker.summary)
        return result[:2000]
