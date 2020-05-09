from InsightSubsystems.Cache.CacheEndpoint.AbstractEmbedEndpoint import AbstractEmbedEndpoint
from InsightUtilities.StaticHelpers import *
from InsightUtilities import EmbedLimitedHelper
import discord
from datetime import datetime, timedelta
import InsightExc
from dateutil.parser import parse as dateTimeParser


class MostExpensiveKMsEmbed(AbstractEmbedEndpoint):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.MostExpensiveKMs = self.cm.MostExpensiveKMs
        self.KMStats = self.cm.KMStats

    @staticmethod
    def default_ttl() -> int:
        return 1800

    @staticmethod
    def _get_unprefixed_key_hash_sync(last_hours: int, server_prefix: str):
        return "{}:{}".format(last_hours, server_prefix)

    async def get(self, last_hours: int = 24, server_prefix: str = "?") -> discord.Embed:
        return await super().get(last_hours=last_hours, server_prefix=server_prefix)

    async def _do_endpoint_logic(self, last_hours: int, server_prefix: str) -> dict:
        top_kms = await self.MostExpensiveKMs.get(batch_limit=25, last_hours=last_hours)
        km_stats = await self.KMStats.get(last_hours=last_hours)
        return await self.executor_proc(self._do_endpoint_logic_sync, last_hours=last_hours,
                                        server_prefix=server_prefix, topkms_dict=top_kms, km_stats=km_stats)

    @classmethod
    def _do_endpoint_logic_sync(cls, last_hours: int, server_prefix: str, topkms_dict: dict, km_stats: dict) -> dict:
        expire_ttl = cls.extract_min_ttl(topkms_dict, km_stats)
        expire = datetime.utcnow() + timedelta(seconds=expire_ttl)
        expire_str = "{} UTC".format(expire.strftime("%H:%M"))
        total_days = int(last_hours / 24) if last_hours > 0 else 0
        time_period_str = "{} days".format(total_days) if total_days > 1 else "{} hours".format(last_hours)
        e = EmbedLimitedHelper()
        e.set_color(cls.default_color())
        e.set_timestamp(datetime.utcnow())
        e.set_title("Most expensive kills over the last {}".format(time_period_str))
        e.set_url("https://zkillboard.com/kills/bigkills/")
        total_kills = "{:,}".format(Helpers.get_nested_value(km_stats, 0, "data", "totalKills"))
        total_value = MathHelper.str_isk(Helpers.get_nested_value(km_stats, 0, "data", "totalValue"), True)
        desc = "Over the last {} there have been a total of **{}** kills worth a total of **{} ISK.**".\
            format(time_period_str, total_kills, total_value)
        e.set_description(desc)
        e.set_author(name="Most Expensive KM Stats", url="https://zkillboard.com/kills/bigkills/",
                     icon_url=URLHelper.type_image(3764, 32))
        e.set_footer(text="Run '{}top help' for additional usages of this command. This command uses cached data "
                          "and the next refresh of the data will be available at {}".format(server_prefix, expire_str))
        tb_set = False
        counter = 1
        for k in Helpers.get_nested_value(topkms_dict, [], "data", "kills"):
            body = ""
            ship_name = Helpers.get_nested_value(k, "", "package", "killmail", "victim", "ship", "type_name")
            ship_id = Helpers.get_nested_value(k, "", "package", "killmail", "victim", "ship", "type_id")
            km_value = MathHelper.str_isk((Helpers.get_nested_value(k, 0, "package", "killmail", "totalValue")))
            km_id = Helpers.get_nested_value(k, 0, "package", "killmail", "killmail_id")
            if not tb_set and ship_id:
                e.set_image(url=URLHelper.type_image(type_id=ship_id, resolution=128))
                tb_set = True
            header = "**{}. {} ({})**".format(counter, ship_name, km_value)
            p_name = Helpers.get_nested_value(k, "", "package", "killmail", "victim", "character", "character_name")
            c_name = Helpers.get_nested_value(k, "", "package", "killmail", "victim", "corporation", "corporation_name")
            a_name = Helpers.get_nested_value(k, "", "package", "killmail", "victim", "alliance", "alliance_name")
            if p_name:
                p_url = URLHelper.zk_pilot(Helpers.get_nested_value(k, "", "package", "killmail", "victim",
                                                                    "character", "character_id"))
                body += "Pilot: [{}]({})\n".format(p_name, p_url)
            if c_name:
                c_url = URLHelper.zk_corporation(Helpers.get_nested_value(k, "", "package", "killmail", "victim",
                                                                          "corporation", "corporation_id"))
                body += "Corp: [{}]({})\n".format(c_name, c_url)
            if a_name:
                a_url = URLHelper.zk_alliance(Helpers.get_nested_value(k, "", "package", "killmail", "victim",
                                                                       "alliance", "alliance"))
                body += "Alliance: [{}]({})\n".format(a_name, a_url)
            system_name = Helpers.get_nested_value(k, "", "package", "killmail", "system", "system_name")
            region_name = Helpers.get_nested_value(k, "", "package", "killmail", "system", "constellation", "region",
                                                   "region_name")
            dt = dateTimeParser(Helpers.get_nested_value(k, datetime.utcnow(), "package", "killmail", "killmail_time"))
            body += "Time: {}\n".format(dt.strftime("%Y-%m-%d %H:%M"))
            dotlan_url = URLHelper.str_dotlan_map(system_name, region_name)
            s = "System: [{}({})]({})\n".format(system_name, region_name, dotlan_url)
            body += s
            body += "**[KM]({})**".format(URLHelper.zk_url(km_id))
            try:
                e.add_field(name=header, value=body, inline=True)
                counter += 1
            except InsightExc.Utilities.EmbedMaxTotalFieldsLimit:
                break
            except InsightExc.Utilities.EmbedMaxTotalCharLimit:
                break
        j = e.to_dict()
        return_result = {
            "embed": j,
        }
        cls.set_min_ttl(return_result, expire_ttl)
        return return_result
