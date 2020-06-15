from .UnboundCommandBase import *
from InsightSubsystems.Cache.CacheEndpoint import InsightMeta
from InsightUtilities.StaticHelpers import Helpers, URLHelper


class Motd(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.InsightMeta: InsightMeta = InsightMeta()

    @classmethod
    def mention(cls):
        return False

    def generate_response(self):
        pass

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs) -> str:
        motd = await self.InsightMeta.get("motd")
        motd_text = await Helpers.async_get_nested_value(motd, "", "data", "data", "value")
        date_modified = await Helpers.async_get_nested_value(motd, datetime.datetime.utcnow(), "data", "modified")
        date_modified_str = date_modified.strftime("%d.%m.%Y %H:%M")
        return_str = "The message of the day was updated at {} UTC\n".format(date_modified_str)
        return_str += "Message of the day:\n\n{}".format(motd_text)
        return return_str

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs):
        e = await super().get_embed(d_message, message_text, **kwargs)
        e.set_thumbnail(url=URLHelper.type_image(24692, 256))
        e.set_footer(text="Insight admins can run !admin to update this motd.")
        return e
