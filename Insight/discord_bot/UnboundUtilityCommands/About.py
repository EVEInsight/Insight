from .UnboundCommandBase import *


class About(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.resp = self.generate_response()

    @classmethod
    def mention(cls):
        return False

    def generate_response(self):
        s = "Insight {} by Nathan-LS. An EVE Online killmail feed bot for Discord.\n\n".format(str(self.service.get_version()))
        s += "Released under the GNU General Public License v3.0\n\n"
        s += "**Links:**\n"
        for l in [
            "[EVEInsight.net](https://eveinsight.net)",
            "[Insight on GitHub](https://github.com/Nathan-LS/Insight)",
            "[Insight on Docker Hub](https://hub.docker.com/r/nathanls/insight/)",
            "[View ChangeLog](https://github.com/Nathan-LS/Insight/blob/master/ChangeLog.md)",
            "[Invite me to your Discord server]({invite_url})",
            "[Join Insight support Discord for additional help](https://discord.gg/Np3FCUn)"
        ]:
            s += "{}\n".format(l)
        s += "\n**Insight utilizes the following third-party libraries:**\n"
        for l in[
            "[discord.py](https://github.com/Rapptz/discord.py/tree/rewrite)",
            "[SQLAlchemy](https://www.sqlalchemy.org/)",
            "[NetworkX](https://github.com/networkx/networkx)",
            "[AIOHTTP](https://aiohttp.readthedocs.io/en/stable/)",
            "[janus](https://github.com/aio-libs/janus)",
            "[Pympler](https://github.com/pympler/pympler)",
            "[cryptography](https://cryptography.io/en/latest/)",
            "[swagger-client](https://github.com/swagger-api/swagger-codegen)"
        ]:
            s += "{}\n".format(l)
        s += "\n**Special thanks:**\n"
        for l in [
            "[Fuzzwork - SDE SQLite conversions](https://www.fuzzwork.co.uk/)",
            "[zKillboard - Websocket and RedisQ killmail API](https://github.com/zKillboard/zKillboard)",
            "[CCP ESI - EVE Online API endpoints](https://esi.evetech.net/ui/)"
        ]:
            s += "{}\n".format(l)
        return s

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs)->str:
        return self.resp.format(invite_url=self.client.get_invite_url())

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs):
        e = await super().get_embed(d_message, message_text, **kwargs)
        e.set_thumbnail(url="https://imageserver.eveonline.com/Character/1326083433_128.jpg")
        return e
