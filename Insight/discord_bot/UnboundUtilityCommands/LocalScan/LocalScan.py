from ..UnboundCommandBase import *
from InsightSubsystems.Cache.CacheEndpoint.LocalScanEmbeds.LocalScanEmbedBase import LocalScanEmbedBase
from InsightUtilities.StaticHelpers import RegexCheck
from functools import partial


class LocalScan(UnboundCommandBase):
    def __init__(self, unbound_service, is_main_command=False):
        super().__init__(unbound_service, is_main_command)
        self.LocalScanEmbedBase = LocalScanEmbedBase()

    def yield_subcommands(self):
        yield ["help", "h"], self.unbound.localscan_help.run_command

    @classmethod
    def mention(cls):
        return False

    def process_character_names(self, message_chars: str):
        return_names = []
        input_names = message_chars.split("\n")
        for char_name in input_names:
            if RegexCheck.is_valid_character_name(char_name):
                return_names.append(char_name)
        return return_names

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) ->discord.Embed:
        valid_names = await self.loop.run_in_executor(None, partial(self.process_character_names, message_text))
        prefix = await self.serverManager.get_min_prefix(d_message.channel)
        return await self.LocalScanEmbedBase.get(char_names=valid_names, server_prefix=prefix)
