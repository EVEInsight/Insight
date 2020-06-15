from ..UnboundCommandBase import *
from . import AdminResetNames, Backup, MemoryDiagnostic, MailExport, SetMotd


class Admin(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.cLock = asyncio.Lock(loop=self.client.loop)
        self.admin_resetnames = AdminResetNames.AdminResetNames(self.unbound)
        self.admin_backup = Backup.Backup(self.unbound)
        self.admin_mem = MemoryDiagnostic.MemoryDiagnostic(self.unbound)
        self.admin_mail_export = MailExport.MailExport(self.unbound)
        self.set_motd = SetMotd.SetMotd(self.unbound)

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        async with self.cLock:
            options = dOpt.mapper_index_withAdditional(self.client, d_message)
            options.set_main_header("Select an Insight administrator function to execute.")
            options.add_option(dOpt.option_calls_coroutine(self.admin_resetnames.command_description(), "",
                                                           self.admin_resetnames.run_command(d_message)))
            options.add_option(dOpt.option_calls_coroutine(self.admin_mem.command_description(), "",
                                                           self.admin_mem.run_command(d_message)))
            options.add_option(dOpt.option_calls_coroutine(self.admin_backup.command_description(), "",
                                                           self.admin_backup.run_command(d_message)))
            options.add_option(dOpt.option_calls_coroutine(self.unbound.quit.command_description(), "",
                                                           self.unbound.quit.run_command(d_message)))
            options.add_option(dOpt.option_calls_coroutine(self.admin_mail_export.command_description(), "",
                                                           self.admin_mail_export.run_command(d_message)))
            options.add_option(dOpt.option_calls_coroutine(self.set_motd.command_description(), "",
                                                           self.set_motd.run_command(d_message)))

            await options()
