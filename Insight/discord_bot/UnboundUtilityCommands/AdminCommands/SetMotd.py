from ..UnboundCommandBase import *
from database.db_tables import tb_meta
from functools import partial
from InsightSubsystems.Cache.CacheEndpoint import InsightMeta


class SetMotd(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.cLock = asyncio.Lock(loop=self.client.loop)
        self.InsightMeta: InsightMeta = InsightMeta()

    def command_description(self):
        return "Set MOTD - Modify the global motd (message of the day)."

    async def set_motd(self, new_motd: str):
        d = {"value": new_motd}
        if await self.loop.run_in_executor(None, partial(tb_meta.set, "motd", d)):
            return await self.InsightMeta.delete_no_fail("motd")
        else:
            return False

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        async with self.cLock:
            options = dOpt.mapper_return_noOptions(self.client, d_message)
            options.set_main_header("Enter the MOTD you wish to set.")
            resp = await options()
            if len(resp) > 0:
                q_text = "The MOTD will be updated to the following:\n\n {} \n\nApprove of this change?".format(resp)
                approve_motd = dOpt.mapper_return_yes_no(self.client, d_message)
                approve_motd.set_main_header(q_text)
                if await approve_motd():
                    update_ok = await self.set_motd(resp)
                    if update_ok:
                        response_text = "The message of the day was successfully updated."
                    else:
                        response_text = "There was an error when updating the message of the day."
                    async with (await LimitManager.cm_hp(d_message.channel)):
                        await d_message.channel.send(response_text)
