from .UnboundCommandBase import *
import os


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
                                    "third-party libraries used by Insight. This update tool will NOT work for "
                                    "versions of Insight that do not use Git and the Python interpreter. You must "
                                    "quit Insight and start it from the command line if there were changes to any of "
                                    "the following project files: \n\n/Insight/__main__.py\n"
                                    "/Insight/InsightMain/InsightMain.py\n/Insight/InsightMain/InsightUpdater.py\n\n"
                                    "\nThis tool will update the Insight Git repo located at the "
                                    "following path to the latest commit for the set branch : \n\n'{}'\n\n "
                                    "You may get a 'CancelledError message in Discord which you can"
                                    " safely ignore.".format(os.getcwd()))
            resp = await options()
            if resp:
                await self.client.update_self(d_message.author)
