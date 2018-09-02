import enum
import datetime
import traceback


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
        self.feed = feed_object
        self.km = km_row
        self.channel = discord_channel_object
        self.filters = overall_filters
        self.feed_options = feed_specific_row
        self.internal_list_options()
        self.embed = discord.Embed()
        self.message_txt = ""
        self.color = discord.Color(800680)
        self.text_only = False

    def get_load_time(self):
        return self.km.loaded_time

    def extract_mention(self):
        return enum_mention.noMention

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

    def make_links(self):
        self.zk_kill = "https://zkillboard.com/kill/{}/".format(str(self.km.kill_id))
        self.system_link = "http://evemaps.dotlan.net/system/{}/".format(self.system_name)

    def make_images(self):
        pass

    def run_filter(self):
        raise NotImplementedError

    def make_vars(self):
        __zk_pilot = "https://zkillboard.com/character/{}/"
        self.ship_name = str(self.km.object_victim.object_ship.type_name)
        self.system_name = self.km.systemName()
        self.region_name = self.km.regionName()
        self.pilot_name = self.km.victim_pilotName()
        self.victimP_zk = __zk_pilot.format(str(self.km.object_victim.character_id))
        self.corp_name = self.km.victim_corpName()
        self.alliance_name = self.km.victim_allianceName()
        self.final_blow = self.km.get_final_blow()
        self.fb_name = self.km.fb_Name(self.final_blow)
        self.fbP_zk = __zk_pilot.format(self.km.fb_pID(self.final_blow))
        self.fb_Corp = self.km.fb_Corp(self.final_blow)
        self.fb_ship = self.km.fb_ship(self.final_blow)
        self.inv_str = self.km.str_attacker_count()
        self.damage_taken = self.km.victim_totalDamage()
        self.isk_lost = self.km.victim_iskLost()
        self.total_involved = str(self.km.get_attacker_count())
        self.min_ago = self.km.str_minutes_ago()

    def make_text_heading(self):
        pass

    def make_header(self):
        raise NotImplementedError

    def make_body(self):
        raise NotImplementedError

    def set_frame_color(self):
        self.embed.color = self.color

    def generate_view(self):
        self.make_vars()
        self.make_links()
        self.make_images()
        self.make_text_heading()
        self.make_header()
        self.make_body()
        self.set_frame_color()

    def __bool__(self):
        try:
            __resp = self.run_filter()
            assert isinstance(__resp,bool)
            if __resp:
                self.generate_view()
            return __resp
        except Exception as ex:
            print(ex)
            print(traceback.print_exc())
            return False

    async def __call__(self, *args, **kwargs):
        if self.text_only == True:
            await self.channel.send(content=self.message_txt)
        else:
            await self.channel.send(content=self.message_txt, embed=self.embed)

    def feed_specific_row_type(cls):
        raise NotImplementedError
        #return tb_enfeed  <example

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
