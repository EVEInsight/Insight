from .LocalScan import LocalScan
from InsightSubsystems.Cache.CacheEndpoint.LocalScanEmbeds.LocalScanEmbedAffiliations import LocalScanEmbedAffiliations
import discord
from functools import partial


class LocalScanAffiliations(LocalScan):
    def __init__(self, unbound_service, is_main_command=False):
        super().__init__(unbound_service, is_main_command)
        self.LocalScanEmbedAffiliations = LocalScanEmbedAffiliations()

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        valid_names = await self.loop.run_in_executor(None, partial(self.process_character_names, message_text))
        prefix = await self.serverManager.get_min_prefix(d_message.channel)
        return await self.LocalScanEmbedAffiliations.get(char_names=valid_names, server_prefix=prefix)
