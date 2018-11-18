from .UnboundCommandBase import *


class Reboot(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.cLock = asyncio.Lock(loop=self.client.loop)

    def command_description(self):
        return "Reboot - Reboot the Insight server service."

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        async with self.cLock:
            options = dOpt.mapper_return_yes_no(self.client, d_message)
            options.set_main_header("Are you sure you want to reboot Insight? This will close the Insight "
                                    "server application and restart it. Note: You may get a 'CancelledError' "
                                    "message in Discord which you can safely ignore.")
            resp = await options()
            if resp:
                await self.client.reboot_self(d_message.author)
