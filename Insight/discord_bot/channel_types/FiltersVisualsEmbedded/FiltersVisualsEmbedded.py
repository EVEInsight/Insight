import enum
import datetime
import traceback
import InsightExc
import asyncio
import InsightLogger
from InsightUtilities import DiscordPermissionCheck, LimitManager
import janus


class internal_options(enum.Enum):
    use_blacklist = True
    use_whitelist = False


class base_visual(object):
    def __init__(self, km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object):
        assert isinstance(km_row,tb_kills)
        assert isinstance(discord_channel_object,discord.TextChannel)
        assert isinstance(overall_filters,tb_channels)
        assert isinstance(feed_specific_row,self.feed_specific_row_type())
        assert isinstance(feed_object, discord_bot.channel_types.insight_feed_service_base)
        self.start_time = InsightLogger.InsightLogger.time_start()
        self.feed = feed_object
        self.km = km_row
        self.km_id = self.km.kill_id
        self.logger = feed_object.logger_filter
        self.channel = discord_channel_object
        self.filters = overall_filters
        self.feed_options = feed_specific_row
        self.internal_list_options()
        self.embed = discord.Embed()
        self.message_txt = ""
        self.color = discord.Color(800680)
        self.text_only = False
        self.send_attempt_count = 0

        self.fb: tb_attackers = None
        self.vi: tb_victims = None
        self.hv: tb_attackers = None
        self.system: tb_systems = None

    def get_load_time(self):
        return self.km.loaded_time

    def extract_mention(self):
        return self.filters.mention

    def mention_method(self):
        if self.feed.can_mention():
            try:
                mention = self.extract_mention()
                if mention != enum_mention.noMention:
                    self.feed.mentioned()
                    return mention.value
            except Exception as ex:
                print(ex)
        return enum_mention.noMention.value

    def internal_list_options(self):
        self.in_system_ly = internal_options.use_blacklist.value
        self.in_system_nonly = internal_options.use_blacklist.value
        self.in_attackers_affiliation = internal_options.use_blacklist.value
        self.in_attackers_ships_type = internal_options.use_blacklist.value
        self.in_attackers_ship_group = internal_options.use_blacklist.value
        self.in_attackers_ships_category = internal_options.use_blacklist.value
        self.in_victim_affiliation = internal_options.use_blacklist.value
        self.in_victim_ship_type = internal_options.use_blacklist.value
        self.in_victim_ship_group = internal_options.use_blacklist.value
        self.in_victim_ship_category = internal_options.use_blacklist.value

    def run_filter(self):
        raise NotImplementedError

    def make_vars(self):
        self.fb: tb_attackers = self.km.get_final_blow()
        self.vi: tb_victims = self.km.get_victim()
        self.hv: tb_attackers = self.fb  # change to hv in child classes
        self.system: tb_systems = self.km.get_system()

        self.embed.url = self.km.str_zk_link()
        self.embed.timestamp = self.km.get_time()

    def make_text_heading(self):
        pass

    def make_header(self):
        raise NotImplementedError

    def make_body(self):
        raise NotImplementedError

    def make_footer(self):
        raise NotImplementedError

    def set_frame_color(self):
        self.embed.color = self.color

    def generate_view(self):
        self.make_vars()
        self.make_text_heading()
        self.make_header()
        self.make_body()
        self.make_footer()
        self.set_frame_color()

    def __bool__(self):
        try:
            __resp = self.run_filter()
            assert isinstance(__resp, bool)
            InsightLogger.InsightLogger.time_log_min(self.logger, self.start_time, "Filter", 1000)
            if __resp:
                self.generate_view()
            return __resp
        except Exception as ex:
            self.logger.exception("km-{}".format(self.km_id))
            print(ex)
            traceback.print_exc()
            return False

    async def __call__(self, *args, **kwargs):
        if self.send_attempt_count >= 5:
            raise InsightExc.DiscordError.MessageMaxRetryExceed
        else:
            self.send_attempt_count += 1
            if self.text_only:
                if DiscordPermissionCheck.can_text(self.channel):
                    async with (await LimitManager.cm(self.channel)):
                        await self.channel.send(content=self.message_txt)
                else:
                    raise InsightExc.DiscordError.DiscordPermissions
            else:
                if DiscordPermissionCheck.can_embed(self.channel):
                    async with (await LimitManager.cm(self.channel)):
                        await self.channel.send(content=self.message_txt, embed=self.embed)
                else:
                    raise InsightExc.DiscordError.DiscordPermissions

    async def queue_task(self, discord_queue: janus.Queue):
        if self.send_attempt_count == 1:
            await asyncio.sleep(60)
        elif self.send_attempt_count == 2:
            await asyncio.sleep(600)
        elif self.send_attempt_count == 3:
            await asyncio.sleep(3600)
        elif self.send_attempt_count == 4:
            await asyncio.sleep(86400)
        else:
            await asyncio.sleep(1)
        await discord_queue.async_q.put(self)

    async def requeue(self, discord_queue):
        self.feed.discord_client.loop.create_task(self.queue_task(discord_queue))

    def debug_info(self):
        return "KM ID: {} Feed: {} AppearanceID: {} TextChannel: {} Attempt: {}".format(self.km_id, type(self.feed), self.appearance_id(),
                                                                          self.channel.id, self.send_attempt_count)

    def feed_specific_row_type(cls):
        raise NotImplementedError
        #return tb_enfeed  <example

    def max_delta(self)->datetime.timedelta:
        return datetime.timedelta(days=7)

    @classmethod
    def get_appearance_class(cls, c_id):
        try:
            for ac in cls.appearance_options():
                if ac.appearance_id() == c_id:
                    return ac
            raise NotImplementedError  # id not programmed
        except Exception as ex:
            if type(ex) == NotImplementedError:
                print("Invalid appearance ID")
            else:
                print(ex)
            return cls

    @classmethod
    def appearance_url(cls) -> str:
        return "https://wiki.eveinsight.net/appearances"

    @classmethod
    def appearance_options(cls):
        yield cls

    @classmethod
    def appearance_id(cls):
        return 0

    @classmethod
    def get_desc(cls):
        return "Full - Detailed overview. Size: Large"


from database.db_tables import *
import discord
import discord_bot.channel_types
