from .UnboundCommandBase import *
from InsightUtilities import MemTracker


class MemoryDiagnostic(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.cLock = asyncio.Lock(loop=self.client.loop)

    def command_description(self):
        return "Memory Diagnostic - Display the largest items in memory."

    def get_text(self, message_text: str):
        return MemTracker.summary()[:2000]
