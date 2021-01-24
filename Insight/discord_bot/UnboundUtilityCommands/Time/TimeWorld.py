from ..UnboundCommandBase import *
from .Time import Time
import discord
from InsightUtilities.EmbedLimitedHelper import EmbedLimitedHelper
from dateutil import tz
import dateutil
from datetime import datetime, timezone


class TimeWorld(Time):
    def __init__(self, unbound_service, is_main_command=False):
        self.tz_iana = [
            ("America/Los_Angeles", "Los Angeles / US Pacific"),
            ("America/Denver", "Denver / US Mountain"),
            ("America/Chicago", "Chicago / US Central"),
            ("America/New_York", "New York / US East"),
            ("America/Caracas", "Caracas", "VET"),
            ("America/Sao_Paulo", "Rio de Janeiro", "BRT"),
            ("Atlantic/Reykjavik", "Reykjavík"),
            ("Europe/London", "London / EU West"),
            ("Europe/Berlin", "Berlin / EU Central"),
            ("Europe/Kiev", "Kiev / EU East"),
            ("Europe/Moscow", "Moscow"),
            ("Asia/Calcutta", "Calcutta"),
            ("Asia/Shanghai", "China Standard Time"),
            ("Australia/Perth", "Perth / AU West"),
            ("Asia/Tokyo", "Tokyo"),
            ("Australia/Darwin", "Darwin / AU Central"),
            ("Australia/Sydney", "Sydney / AU East"),
            ("Pacific/Auckland", "New Zealand")

        ]
        self.tzs = []
        self.tz_loader()
        super().__init__(unbound_service, is_main_command)

    def tz_loader(self):
        for t in self.tz_iana:
            tz_data = tz.gettz(t[0])
            try:
                tz_abbreviation_override = t[2]
            except IndexError:
                tz_abbreviation_override = ""
            if isinstance(tz_data, dateutil.tz.tzfile):
                self.tzs.append((tz_data, t[1], tz_abbreviation_override))
            else:
                print("TZ Loader error when attempting to load tz data for TZ: {}".format(t[0]))

    def make_embed_calc_times(self, prefix):
        ct = datetime.now(timezone.utc)
        e = EmbedLimitedHelper()
        e.set_color(discord.Color(0x49b0b6))
        e.set_timestamp(datetime.utcnow())
        e.set_author(name="World Times")
        e.set_description(description="The current EVE date and time is **{} (UTC)**.\n\n".format(self.format_time(ct)))
        e.field_buffer_start("Time Zones:", "-")
        e.field_buffer_start_bounds("```", "```")
        for t in self.tzs:
            tz_data = t[0]
            tz_desc = t[1]
            tz_abbreviation_override = t[2]
            dt_tz = ct.astimezone(tz_data)
            dt_str = self.format_time(dt_tz, "%Y-%m-%d %H:%M")
            tz_name = self.format_time(dt_tz, "%Z") if not tz_abbreviation_override else tz_abbreviation_override
            str_tz_info = "{} ({})".format(tz_desc, tz_name)
            s = "{:<32} {} ".format(str_tz_info, dt_str)
            e.field_buffer_add(s)
        e.field_buffer_end_bounds()
        e.field_buffer_end()
        e.set_footer(text="Run '{}time help' for additional command usage.".format(prefix))
        return e

    @classmethod
    def embed_only(cls):
        return True

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        prefix = await self.serverManager.get_min_prefix(d_message.channel)
        return await self.loop.run_in_executor(None, partial(self.make_embed_calc_times, prefix))


