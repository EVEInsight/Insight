from .Top import Top
import discord


class TopYear(Top):
    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        return await self.get_top_embed(hour_range=8760, d_message=d_message)

