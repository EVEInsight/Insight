from .FiltersVisualsEmbedded import *


class visual_capradar(base_visual):

    def __init__(self, km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object):
        super(visual_capradar, self).__init__(km_row, discord_channel_object, overall_filters, feed_specific_row,
                                              feed_object)
        assert isinstance(self.feed_options, tb_capRadar)

    def make_links(self):
        super().make_links()
        self.haZK = "https://zkillboard.com/character/{}/".format(self.km.fb_pID(self._highestAT))

    def make_images(self):
        super().make_images()
        if self._highestAT.alliance_id is not None:
            self.thumbnail = "https://imageserver.eveonline.com/Alliance/{}_128.png".format \
                (str(self._highestAT.alliance_id))
        else:
            self.thumbnail = "https://imageserver.eveonline.com/Corporation/{}_128.png".format(
                str(self._highestAT.corporation_id))
        self.ship_image = "https://imageserver.eveonline.com/Render/{}_128.png".format(
            str(self._highestAT.ship_type_id))

    def internal_list_options(self):
        super(visual_capradar, self).internal_list_options()
        self.in_attackers_affiliation = internal_options.use_blacklist.value
        self.in_attackers_ship_group = internal_options.use_whitelist.value
        self.in_system_ly = internal_options.use_whitelist.value

    def make_vars(self):
        super(visual_capradar, self).make_vars()
        self._highestAT = self.km.get_highest_attacker(self.tracked_hostiles)
        self.haName = self.km.fb_Name(self._highestAT)
        self.haCorp = self.km.fb_Corp(self._highestAT)
        self.haAli = self.km.fb_Alliance(self._highestAT, True)
        self.haShip = self.km.fb_ship(self._highestAT)
        self.ha_group = self.km.fb_ShipGroup(self._highestAT)
        self.location_name = self.km.str_location_name()
        self.base_name = str(self.base_.name)
        self._ly_range = self.km.str_ly_range(self.base_)
        self._attacking_ships = self.km.str_overview_attacking_capitals(self.tracked_hostiles)
        self.text_minutes_ago = self.km.str_minutes_ago(True)
        self.overview_text = "{hSG} activity in {kmSys}({kmRg}) {ly} LYs from {bSys}". \
            format(hSG=self.ha_group, kmSys=self.system_name, kmRg=self.region_name, ly=self._ly_range,
                   bSys=self.base_name)

    def extract_mention(self):
        assert isinstance(self._highestAT, tb_attackers)
        for c in self.list_typeGroup:
            if self._highestAT.compare_filter_list(c):
                return c.mention
        return enum_mention.noMention

    def make_text_heading(self):
        self.message_txt = "{} {} {}".format(self.mention_method(), self.overview_text, self.min_ago)

    def make_header(self):
        self.embed.set_author(name=self.overview_text, url=self.zk_kill)
        __desc = '**{ship_name}** destroyed in **[{system_name}]' \
                 '({system_link})**({region_name}) {mAgo}{lName}\n\n' \
                 '*Involving **[{hName}]({haZK})({hCorp})**{hAl} in a **{hShip}** {inv}.*' \
            .format(ship_name=self.ship_name, system_name=self.system_name, system_link=self.system_link,
                    region_name=self.region_name, mAgo=self.text_minutes_ago, lName=self.location_name,
                    hName=self.haName,
                    haZK=self.haZK, hCorp=self.haCorp, hAl=self.haAli, hShip=self.haShip, inv=self.inv_str)
        self.embed.description = __desc
        self.embed.title = " "
        self.embed.url = self.zk_kill
        self.embed.set_thumbnail(url=self.thumbnail)
        self.embed.set_image(url=self.ship_image)
        self.embed.timestamp = self.km.killmail_time

    def make_body(self):
        __heading = "**{} of {} attackers flying in tracked ships:**".format(str(len(self.tracked_hostiles)),
                                                                             str(self.total_involved))
        __body = "```{}```".format(self._attacking_ships, zk=self.zk_kill)
        self.embed.add_field(name=__heading, value=__body, inline=False)
        __heading_routes = "Dotlan routes from {}".format(self.base_name)
        self.embed.add_field(name=__heading_routes, value=self.__helper_routes(), inline=False)
        self.embed.color = discord.Color(800680)

    def set_frame_color(self):
        s = (datetime.datetime.utcnow() - self.km.killmail_time).total_seconds()
        if 0 <= s <= 60:
            self.color = discord.Color(12124259)
        elif 60 <= s <= 300:
            self.color = discord.Color(8454210)
        else:
            self.color = discord.Color(4128800)
        super().set_frame_color()

    def __helper_routes(self):
        _dotlan_link = "http://evemaps.dotlan.net/jump/{ship},555/{base}:{target}".format(ship="{2}",
                                                                                          base=self.base_name,
                                                                                          target=self.system_name)
        _dotlan_gates = "http://evemaps.dotlan.net/route/{base}:{target}".format(base=self.base_name,
                                                                                 target=self.system_name)
        _row = "[```{0:<23}{1}```]" + "({})".format(_dotlan_link)
        _return_str = ""
        _return_str += _row.format("Titans/Supers", "", "Avatar")
        _return_str += _row.format("Carriers/Dreads/FAX", "", "Archon")
        _return_str += _row.format("Blops", "", "Redeemer")
        _return_str += "[```{0:<23}```]({1})\n**{2}**".format("Gates", _dotlan_gates, self.zk_kill)
        return _return_str

    def run_filter(self):
        tdiff = datetime.datetime.utcnow() - datetime.timedelta(minutes=self.feed_options.max_km_age)
        if tdiff >= self.km.killmail_time:
            return False
        self.base_ = self.km.filter_system_ly(self.filters.object_filter_systems, self.in_system_ly)
        if self.base_ is None:
            return False
        self.list_typeGroup = self.filters.object_filter_groups + self.filters.object_filter_types
        tracked_ships = self.km.filter_attackers(self.km.object_attackers, self.list_typeGroup,
                                                 self.in_attackers_ship_group)
        if len(tracked_ships) == 0:
            return False
        __list_aff = self.filters.object_filter_alliances + self.filters.object_filter_corporations + self.filters.object_filter_characters
        self.tracked_hostiles = self.km.filter_attackers(tracked_ships, __list_aff, self.in_attackers_affiliation)
        if len(self.tracked_hostiles) == 0:
            return False
        return True

    @classmethod
    def feed_specific_row_type(cls):
        return tb_capRadar

    @classmethod
    def appearance_options(cls):
        yield cls
        yield VisualCapRadarCompact
        yield VisualCapRadarLinkOnly

    @classmethod
    def get_desc(cls):
        return "Full - Full overview of tracked shiptypes, Dotlan routes, images, color time indicator sidebar, and images. Size: Large"


from .VisualCapRadarCompact import VisualCapRadarCompact
from .VisualCapRadarLinkOnly import VisualCapRadarLinkOnly
