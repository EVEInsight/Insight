from .Top import Top
import discord


class TopWeek(Top):
    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        return await self.get_top_embed(hour_range=168, d_message=d_message)

