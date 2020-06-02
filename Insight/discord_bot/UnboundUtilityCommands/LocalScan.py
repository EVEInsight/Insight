from .UnboundCommandBase import *
from InsightSubsystems.Cache.CacheEndpoint.LocalScanEmbeds.LocalScanEmbedBase import LocalScanEmbedBase
from InsightUtilities.StaticHelpers import RegexCheck
from functools import partial


class LocalScan(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.LocalScanEmbedBase = LocalScanEmbedBase()

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
        return await self.LocalScanEmbedBase.get(char_names=valid_names)
