from InsightSubsystems.Cache.CacheEndpoint.AbstractEmbedEndpoint import AbstractEmbedEndpoint
from InsightUtilities.StaticHelpers import *
from InsightUtilities import EmbedLimitedHelper
import discord
from datetime import datetime
from statistics import mean
from math import floor


class LocalScanEmbedBase(AbstractEmbedEndpoint):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.LocalScan = self.cm.LocalScan

    @staticmethod
    def default_ttl() -> int:
        return 30

    @classmethod
    def buffer_character(cls):
        return 20

    @classmethod
    def buffer_ship(cls):
        return 25

    @classmethod
    def get_buffer_len(cls, avg_len, max_len, buffer_max):
        if max_len + 1 <= buffer_max:
            return max_len + 1
        else:
            mid_len = int(avg_len + max_len / 2)
            if mid_len <= buffer_max:
                return mid_len
            else:
                return buffer_max

    @staticmethod
    def _get_unprefixed_key_hash_sync(char_names: frozenset, seconds_ago_threshold: int, server_prefix: str):
        return "{}:{}:{}".format(seconds_ago_threshold, hash(char_names), server_prefix)

    async def get(self, char_names: list, server_prefix: str) -> discord.Embed:
        set_char_names = await self.executor(self.make_frozen_set, list_items=char_names)
        seconds_ago_threshold = int(1e+10)
        return await super().get(char_names=set_char_names, seconds_ago_threshold=seconds_ago_threshold,
                                 server_prefix=server_prefix)

    async def _do_endpoint_logic(self, char_names: frozenset, seconds_ago_threshold: int, server_prefix: str) -> dict:
        local_scan = await self.LocalScan.get(char_names=char_names, seconds_ago_threshold=seconds_ago_threshold)
        return await self.executor(self._do_endpoint_logic_sync, scan=local_scan, server_prefix=server_prefix)

    @classmethod
    def get_alert_prefixed_ship(cls, is_super_titan, is_cap, base_ship_value):
        if is_super_titan or base_ship_value >= 15e+9:  # alert if super or ship hull is 10b+
            return "❗"
        elif is_cap or base_ship_value >= 7.5e+9:
            return "❕"
        else:
            return ""

    @classmethod
    def _add_pilot_ship(cls, e: EmbedLimitedHelper, scan: dict, char_id: int, buffer_char, buffer_ship):
        char_data = Helpers.get_nested_value(scan, {}, "characters", char_id)
        char_name = Helpers.get_nested_value(char_data, "", "characterName")[:14]
        is_attacker = Helpers.get_nested_value(char_data, True, "attacker")
        is_super_titan = Helpers.get_nested_value(char_data, False, "isSuperTitan")
        is_regular_cap = Helpers.get_nested_value(char_data, False, "isRegularCap")
        ship_id = Helpers.get_nested_value(char_data, 0, "shipID")
        ship_name = Helpers.get_nested_value(scan, "UNKNOWN", "ships", ship_id, "ship", "type_name")
        base_ship_value = Helpers.get_nested_value(scan, 0, "ships", ship_id, "ship", "basePrice")
        delta_seconds = Helpers.get_nested_value(char_data, 0, "seconds")
        delta_str = MathHelper.str_min_seconds_convert(delta_seconds)
        ship_name_str = cls.get_alert_prefixed_ship(is_super_titan, is_regular_cap, base_ship_value)
        ship_name_str += (ship_name if is_attacker else "(L){}".format(ship_name))
        field_line = "{:<{len_char}} {:<{len_ship}} {}".format(char_name[:buffer_char], ship_name_str[:buffer_ship],
                                                               delta_str, len_char=buffer_char, len_ship=buffer_ship)
        e.field_buffer_add(field_line)

    @classmethod
    def _add_summary_involved_mails(cls, e: EmbedLimitedHelper, scan: dict, zk_ratios: dict, max_to_post=3,
                                    ratio_threshold=.35, first_ratio=.1):
        km_ratios_added = 0
        for km in zk_ratios:
            if km_ratios_added >= max_to_post:
                break
            ratio = Helpers.get_nested_value(km, 0, "ratio")
            if (ratio >= ratio_threshold and km_ratios_added > 0) or \
                    (ratio >= first_ratio and km_ratios_added == 0):
                km_percent = MathHelper.percent_convert(ratio)
                km_id = Helpers.get_nested_value(km, 0, "kmID")
                km_data = Helpers.get_nested_value(scan, {}, "kms", km_id, "km")
                zk_ship_name_lost = Helpers.get_nested_value(km_data, "UNKNOWN", "victim", "ship", "type_name")
                zk_url = Helpers.get_nested_value(km_data, "https://zkillboard.com", "urlZK")
                system_name = Helpers.get_nested_value(km_data, 'UNKNOWN', "system", "system_name")
                system_url = Helpers.get_nested_value(km_data, "http://evemaps.dotlan.net", "system", "urlDotlanMap")
                km_str = "**[{}]({})** in [{}]({}) {}".format(zk_ship_name_lost, zk_url, system_name, system_url,
                                                            km_percent)
                if km_ratios_added == 0:
                    e.field_buffer_end_bounds()
                    header_str = "KMs:"
                    if e.check_remaining_lower_limits(len(header_str) + len(km_str) + 30, 2):
                        break
                    e.field_buffer_add(header_str)
                if e.check_remaining_lower_limits(len(km_str) + 30, 2):
                    break
                e.field_buffer_add(km_str)
                km_ratios_added += 1

    @classmethod
    def get_header_str(cls, scan: dict):
        total_alive = Helpers.get_nested_value(scan, 0, "totalAlive")
        total_dead = Helpers.get_nested_value(scan, 0, "totalDead")
        total_unknown = Helpers.get_nested_value(scan, 0, "totalUnknown")
        total_unknown_names = Helpers.get_nested_value(scan, 0, "totalUnknownNames")
        str_stats = "--Totals:\n"
        str_stats += "" if not total_alive else "Alive: {}\n".format(total_alive)
        str_stats += "" if not total_dead else "Dead: {}\n".format(total_dead)
        str_stats += "" if not total_unknown else "Unknown: {}\n".format(total_unknown)
        str_stats += "" if not total_unknown_names else "Unknown Name / No KB Activity: {}\n".format(total_unknown_names)
        return str_stats


    @classmethod
    def _do_endpoint_logic_sync(cls, scan: dict, server_prefix: str) -> dict:
        list_all_character_ids = Helpers.get_nested_value(scan, {}, "characters").keys()
        set_all_character_ids = set(list_all_character_ids)
        e = EmbedLimitedHelper()
        e.set_color(cls.default_color())
        e.set_timestamp(datetime.utcnow())
        str_stats = cls.get_header_str(scan)
        char_str_buffer_totals = []
        ship_str_buffer_totals = []
        e.set_description("Pilots are listed based on recent activity, a timestamp and if the last activity "
                          "was a loss (L). Location refers to nearest celestial and may not represent where activity "
                          "occurred (AU distances are omitted). \n\n{}".format(str_stats))
        e.set_author(name="Scan of {} pilots".format(Helpers.get_nested_value(scan, 0, "totalQueried")),
                     icon_url=URLHelper.type_image(1973, 64))
        e.set_footer(text="Run '{}s -h' for additional help and usage.".format(server_prefix))
        alliances = Helpers.get_nested_value(scan, [], "alliances")
        corporations = Helpers.get_nested_value(scan, [], "corporations")
        global_tabbed_grps = 0
        for grp in list(alliances.values()) + list(corporations.values()):
            strShipAvg = Helpers.get_nested_value(grp, 0, "strShipAvg")
            strShipMax = Helpers.get_nested_value(grp, 0, "strShipMax")
            ship_str_buffer = cls.get_buffer_len(avg_len=strShipAvg, max_len=strShipMax+3, buffer_max=cls.buffer_ship())
            ship_str_buffer_totals.append(ship_str_buffer)
            strCharAvg = Helpers.get_nested_value(grp, 0, "strCharNameAvg")
            strCharMax = Helpers.get_nested_value(grp, 0, "strCharNameMax")
            char_str_buffer = cls.get_buffer_len(avg_len=strCharAvg, max_len=strCharMax+3, buffer_max=cls.buffer_character())
            char_str_buffer_totals.append(char_str_buffer)
            if global_tabbed_grps >= 5:
                break
            if e.check_remaining_lower_limits_ratio(.15, .15):
                break
            global_tabbed_grps += 1
            list_grp_character_ids = Helpers.get_nested_value(grp, {}, "characters").keys()
            set_grp_character_ids = set(list_grp_character_ids)
            grp_alive = Helpers.get_nested_value(grp, 0, "totalAlive")
            grp_dead = Helpers.get_nested_value(grp, 0, "totalDead")
            grp_name = Helpers.get_nested_value(grp, "", "name")[:int(e.limit_field_name * .5)]
            header = "**{} -- Alive:{} Dead:{}**".format(grp_name, grp_alive, grp_dead)
            e.field_buffer_start(name=header, name_continued="{} -- Continued".format(grp_name), inline=False)
            e.field_buffer_start_bounds("```\n", "\n```")
            grp_tabbed_systems = 0
            grp_tabbed_locations = 0
            for system_ratio in Helpers.get_nested_value(grp, {}, "systems").values():
                if grp_tabbed_systems >= 3:
                    break
                if e.check_remaining_lower_limits_ratio(.25, .25):
                    break
                grp_tabbed_systems += 1
                system_id = Helpers.get_nested_value(system_ratio, 0, "systemID")
                system_data = Helpers.get_nested_value(scan, {}, "systems", system_id)
                system_name = Helpers.get_nested_value(system_data, "UNKNOWN SYSTEM", "system", "system_name")
                e.field_buffer_add("-{}".format(system_name))
                for location_id in Helpers.get_nested_value(system_ratio, [], "locationIDs"):
                    if grp_tabbed_locations >= 3:
                        break
                    if e.check_remaining_lower_limits_ratio(.25, .25):
                        break
                    grp_tabbed_locations += 1
                    location_data = Helpers.get_nested_value(scan, {}, "locations", location_id)
                    location_name = Helpers.get_nested_value(location_data, "UNKNOWN LOCATION", "location",
                                                             "location_name")
                    character_ids_location = Helpers.get_nested_value(grp, [], "locations", location_id, "characterIDs")
                    e.field_buffer_add("--{}".format(location_name))
                    for character_id in character_ids_location:
                        if e.check_remaining_lower_limits_ratio(.10, .10):
                            break
                        cls._add_pilot_ship(e, scan, character_id, char_str_buffer, ship_str_buffer)
                        set_grp_character_ids.remove(character_id)
                        set_all_character_ids.remove(character_id)
                    e.field_buffer_add("")
            if len(set_grp_character_ids) > 0:
                e.field_buffer_add("-Misc Locations")
                for character_id in list_grp_character_ids:
                    if character_id in set_grp_character_ids:
                        if e.check_remaining_lower_limits_ratio(.10, .10):
                            break
                        cls._add_pilot_ship(e, scan, character_id, char_str_buffer, ship_str_buffer)
                        set_grp_character_ids.remove(character_id)
                        set_all_character_ids.remove(character_id)
                e.field_buffer_end_bounds()
            km_ratios = Helpers.get_nested_value(grp, {}, "kms").values()
            cls._add_summary_involved_mails(e, scan, km_ratios, max_to_post=3, ratio_threshold=.25)
            e.field_buffer_end()
        if len(set_all_character_ids) > 0:
            char_str_buffer = floor(mean(char_str_buffer_totals))
            ship_str_buffer = floor(mean(ship_str_buffer_totals))
            e.field_buffer_start("Misc Affiliation", name_continued="Misc Affiliation", inline=False)
            e.field_buffer_start_bounds("", "")
            e.field_buffer_add("Pilots not in highest concentration of alliances or corporations.")
            e.field_buffer_end_bounds()
            e.field_buffer_start_bounds("```\n", "\n```")
            for character_id in list_all_character_ids:
                if character_id in set_all_character_ids:
                    if e.check_remaining_lower_limits(75, 1):
                        break
                    cls._add_pilot_ship(e, scan, character_id, char_str_buffer, ship_str_buffer)
                    set_all_character_ids.remove(character_id)
            if len(set_all_character_ids) > 0:
                e.field_buffer_add("----Truncated {}".format(len(set_all_character_ids)))
                if len(set_all_character_ids) > 15:
                    line_subc = "Note: Use \"{}s -a\" to display ship counts grouped by alliances/corps.".\
                        format(server_prefix)
                    if e.check_line_fits(line_subc):
                        e.field_buffer_add(line_subc)
            e.field_buffer_end_bounds()
            km_ratios = Helpers.get_nested_value(scan, {}, "kms").values()
            cls._add_summary_involved_mails(e, scan, km_ratios, max_to_post=3, ratio_threshold=.35)
            e.field_buffer_end()
        return_result = {
            "embed": e.to_dict(),
        }
        return return_result

