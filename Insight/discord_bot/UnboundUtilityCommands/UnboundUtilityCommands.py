from . import Dscan, EightBall, Quit, Admin, AdminResetNames, Backup, Reboot, Update, MemoryDiagnostic, Prefix, About, \
    Help, MailExport
import discord
import discord_bot


class UnboundUtilityCommands(object):
    def __init__(self, insight_client):
        assert isinstance(insight_client, discord_bot.Discord_Insight_Client)
        self.client: discord_bot.Discord_Insight_Client = insight_client
        self.serverManager = self.client.serverManager
        self.commandParser = self.client.commandLookup
        self.threadpool_unbound = self.client.threadpool_unbound
        self.dscan = Dscan.Dscan(self)
        self.eightBall = EightBall.EightBall(self)
        self.prefix = Prefix.Prefix(self)
        self.about = About.About(self)
        self.help = Help.Help(self)
        self.quit = Quit.Quit(self)
        self.admin = Admin.Admin(self)
        self.admin_resetnames = AdminResetNames.AdminResetNames(self)
        self.admin_backup = Backup.Backup(self)
        self.admin_reboot = Reboot.Reboot(self)
        self.admin_update = Update.Update(self)
        self.admin_mem = MemoryDiagnostic.MemoryDiagnostic(self)
        self.admin_mail_export = MailExport.MailExport(self)

    async def strip_command(self, message_object: discord.Message):
        prefixes = await self.serverManager.get_server_prefixes(message_object.channel)
        return self.commandParser.strip_non_command(prefixes, message_object.content)

    async def command_dscan(self, message_object: discord.Message):
        await self.dscan.run_command(message_object, await self.strip_command(message_object))

    async def command_8ball(self, message_object: discord.Message):
        await self.eightBall.run_command(message_object, await self.strip_command(message_object))

    async def command_quit(self, message_object: discord.Message):
        await self.quit.run_command(message_object, await self.strip_command(message_object))

    async def command_admin(self, message_object: discord.Message):
        await self.admin.run_command(message_object, await self.strip_command(message_object))

    async def command_prefix(self, message_object: discord.Message):
        await self.prefix.run_command(message_object, await self.strip_command(message_object))

    async def command_about(self, message_object: discord.Message):
        await self.about.run_command(message_object, await self.strip_command(message_object))

    async def command_help(self, message_object: discord.Message):
        await self.help.run_command(message_object, await self.strip_command(message_object))
