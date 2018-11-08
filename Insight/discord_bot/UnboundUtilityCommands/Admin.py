from .UnboundCommandBase import *


class Admin(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.cLock = asyncio.Lock(loop=self.client.loop)

    async def run_command(self, d_message: discord.Message, m_text: str):
        async with self.cLock:
            options = dOpt.mapper_index_withAdditional(self.client, d_message)
            options.set_main_header("Select an Insight administrator function to execute.")
            options.add_option(dOpt.option_calls_coroutine(self.unbound.quit.command_description(), "", self.unbound.command_quit(d_message)))
            await options()
