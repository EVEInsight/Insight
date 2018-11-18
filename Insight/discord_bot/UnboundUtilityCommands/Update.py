from .UnboundCommandBase import *


class Update(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.cLock = asyncio.Lock(loop=self.client.loop)

    def command_description(self):
        return "Update - Update Insight using Git. This feature is unavailable for bin versions of Insight."

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        async with self.cLock:
            options = dOpt.mapper_return_yes_no(self.client, d_message)
            options.set_main_header("Are you sure you want to update Insight? This will reboot the Insight "
                                    "server application and update it.\n\nWARNING: This will NOT update or install new "
                                    "third-party libraries used by Insight. Ensure 'requirements.txt' has not "
                                    "changed in this new patch otherwise you must manually install the new packages"
                                    " to your python interpreter first.\n\nNote: You may get a 'CancelledError' "
                                    "message in Discord which you can safely ignore.")
            resp = await options()
            if resp:
                await self.client.update_self(d_message.author)
