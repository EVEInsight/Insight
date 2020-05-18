from InsightSubsystems.Cache.CacheEndpoint.AbstractEmbedEndpoint import AbstractEmbedEndpoint
from InsightUtilities.StaticHelpers import *
from InsightUtilities import EmbedLimitedHelper
import discord
from datetime import datetime


class LocalScanEmbedBase(AbstractEmbedEndpoint):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.LocalScan = self.cm.LocalScan

    @staticmethod
    def default_ttl() -> int:
        return 30

    @staticmethod
    def _get_unprefixed_key_hash_sync(char_names: frozenset, seconds_ago_threshold: int):
        return "{}:{}".format(seconds_ago_threshold, hash(char_names))

    async def get(self, char_names: list) -> discord.Embed:
        set_char_names = await self.executor_thread(self.make_frozen_set, list_items=char_names)
        seconds_ago_threshold = 1e+10
        return await super().get(char_names=set_char_names, seconds_ago_threshold=seconds_ago_threshold)

    async def _do_endpoint_logic(self, char_names: frozenset, seconds_ago_threshold: int) -> dict:
        local_scan = await self.LocalScan.get(char_names=char_names, seconds_ago_threshold=seconds_ago_threshold)
        return await self.executor_proc(self._do_endpoint_logic_sync, scan=local_scan)

    @classmethod
    def _add_pilot_ship(cls, e: EmbedLimitedHelper, scan: dict, char_id: int):
        char_data = Helpers.get_nested_value(scan, {}, "characters", char_id)
        char_name = Helpers.get_nested_value(char_data, "", "characterName")[:14]
        is_attacker = Helpers.get_nested_value(char_data, True, "attacker")
        ship_id = Helpers.get_nested_value(char_data, 0, "shipID")
        ship_name = Helpers.get_nested_value(scan, "UNKNOWN", "ships", ship_id, "ship", "type_name")
        delta_seconds = Helpers.get_nested_value(char_data, 0, "seconds")
        delta_str = MathHelper.str_min_seconds_convert(delta_seconds)
        ship_name_str = (ship_name if is_attacker else "(DEAD){}".format(ship_name))[:14]
        field_line = "{:<15}{:<15}{}".format(char_name, ship_name_str, delta_str)
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
                    header_str = "Involved KMs:"
                    if e.check_remaining_lower_limits(len(header_str) + len(km_str) + 3, 2):
                        break
                    e.field_buffer_add("Involved KMs:")
                if e.check_remaining_lower_limits(len(km_str) + 3, 2):
                    break
                e.field_buffer_add(km_str)
                km_ratios_added += 1

    @classmethod
    def _do_endpoint_logic_sync(cls, scan: dict) -> dict:
        list_all_character_ids = Helpers.get_nested_value(scan, {}, "characters").keys()
        set_all_character_ids = set(list_all_character_ids)
        e = EmbedLimitedHelper()
        e.set_color(cls.default_color())
        e.set_timestamp(datetime.utcnow())
        total_alive = Helpers.get_nested_value(scan, 0, "totalAlive")
        total_dead = Helpers.get_nested_value(scan, 0, "totalDead")
        total_unknown = Helpers.get_nested_value(scan, 0, "totalUnknown")
        total_unknown_names = Helpers.get_nested_value(scan, 0, "totalUnknownNames")
        str_stats = "--Totals:\n"
        str_stats += "" if not total_alive else "Alive: {}\n".format(total_alive)
        str_stats += "" if not total_dead else "Dead: {}\n".format(total_dead)
        str_stats += "" if not total_unknown else "Unknown: {}\n".format(total_unknown)
        str_stats += "" if not total_unknown_names else "Unknown Name / No KB Activity: {}\n".format(total_unknown_names)
        e.set_description("Pilots are listed with the most recent ship used, a timestamp and if their last activity "
                          "was a loss (DEAD).\n\n{}".format(str_stats))
        e.set_author(name="Scan of {} pilots".format(Helpers.get_nested_value(scan, 0, "totalQueried")),
                     icon_url=URLHelper.type_image(1952, 64))
        e.set_footer(text="Run '!lscan help' for additional help and usage.")
        alliances = Helpers.get_nested_value(scan, [], "alliances")
        corporations = Helpers.get_nested_value(scan, [], "corporations")
        global_tabbed_grps = 0
        for grp in list(alliances.values()) + list(corporations.values()):
            if global_tabbed_grps >= 5:
                break
            if e.check_remaining_lower_limits_ratio(.20, .20):
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
                if e.check_remaining_lower_limits_ratio(.60, .60):
                    break
                grp_tabbed_systems += 1
                system_id = Helpers.get_nested_value(system_ratio, 0, "systemID")
                system_data = Helpers.get_nested_value(scan, {}, "systems", system_id)
                system_name = Helpers.get_nested_value(system_data, "UNKNOWN SYSTEM", "system", "system_name")
                e.field_buffer_add("-{}".format(system_name))
                for location_id in Helpers.get_nested_value(system_ratio, [], "locationIDs"):
                    if grp_tabbed_locations >= 3:
                        break
                    if e.check_remaining_lower_limits_ratio(.60, .60):
                        break
                    grp_tabbed_locations += 1
                    location_data = Helpers.get_nested_value(scan, {}, "locations", location_id)
                    location_name = Helpers.get_nested_value(location_data, "UNKNOWN LOCATION", "location",
                                                             "location_name")
                    character_ids_location = Helpers.get_nested_value(grp, [], "locations", location_id, "characterIDs")
                    e.field_buffer_add("--{}".format(location_name))
                    for character_id in character_ids_location:
                        if e.check_remaining_lower_limits_ratio(.40, .40):
                            break
                        cls._add_pilot_ship(e, scan, character_id)
                        set_grp_character_ids.remove(str(character_id))
                        set_all_character_ids.remove(str(character_id))
                    e.field_buffer_add("")
            if len(set_grp_character_ids) > 0:
                e.field_buffer_add("-Misc Locations")
                for character_id in list_grp_character_ids:
                    if character_id in set_grp_character_ids:
                        if e.check_remaining_lower_limits_ratio(.15, .15):
                            break
                        cls._add_pilot_ship(e, scan, character_id)
                        set_grp_character_ids.remove(str(character_id))
                        set_all_character_ids.remove(str(character_id))
                e.field_buffer_end_bounds()
            km_ratios = Helpers.get_nested_value(grp, {}, "kms").values()
            cls._add_summary_involved_mails(e, scan, km_ratios, max_to_post=3, ratio_threshold=.25)
            e.field_buffer_end()
        if len(set_all_character_ids) > 0:
            e.field_buffer_start("Misc Affiliation", name_continued="Misc Affiliation", inline=False)
            e.field_buffer_start_bounds("", "")
            e.field_buffer_add("Pilots not in highest concentration of alliances or corporations.")
            e.field_buffer_end_bounds()
            e.field_buffer_start_bounds("```\n", "\n```")
            for character_id in list_all_character_ids:
                if character_id in set_all_character_ids:
                    if e.check_remaining_lower_limits(350, 2):
                        break
                    cls._add_pilot_ship(e, scan, character_id)
                    set_all_character_ids.remove(str(character_id))
            if len(set_all_character_ids) > 0:
                e.field_buffer_add("----Truncated {}".format(len(set_all_character_ids)))
            e.field_buffer_end_bounds()
            km_ratios = Helpers.get_nested_value(scan, {}, "kms").values()
            cls._add_summary_involved_mails(e, scan, km_ratios, max_to_post=3, ratio_threshold=.35)
            e.field_buffer_end()
        return_result = {
            "embed": e.to_dict(),
        }
        cls.set_min_ttl(return_result, cls.extract_min_ttl(scan))
        return return_result

