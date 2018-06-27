from .FiltersVisualsEmbedded import *


class visual_enfeed(base_visual):

    def __init__(self, km_row, discord_channel_object, overall_filters, feed_specific_row):
        super(visual_enfeed, self).__init__(km_row, discord_channel_object, overall_filters, feed_specific_row)
        assert isinstance(self.feed_options, tb_enfeed)

    def set_links_images(self):
        self.__zk_kill = "https://zkillboard.com/kill/{}/".format(str(self.km.kill_id))
        if self.km.object_victim.alliance_id is not None:
            self.__im_victim_corpAli = "https://imageserver.eveonline.com/Alliance/{}_128.png".format\
                (str(self.km.object_victim.alliance_id))
        else:
            self.__im_victim_corpAli = "https://imageserver.eveonline.com/Alliance/{}_128.png".format(
                str(self.km.object_victim.corporation_id))

    def internal_list_options(self):
        super(visual_enfeed, self).internal_list_options()
        self.in_attackers_affiliation = internal_options.use_whitelist.value

    def __set_loss(self):
        self.embed.color = discord.Color(16711680) #red
        self.embed.set_author(name="Loss", url=self.__zk_kill, icon_url=self.__im_victim_corpAli)

    def __set_kill(self):
        self.embed.color = discord.Color(65299) #green
        self.embed.set_author(name="Kill",url=self.__zk_kill,icon_url=self.__im_victim_corpAli)

    def __make_vars(self):
        __zk_pilot = "https://zkillboard.com/character/{}/"
        self.ship_name = str(self.km.object_victim.object_ship.type_name)
        self.system_name = self.km.systemName()
        self.system_link = "http://evemaps.dotlan.net/system/{}/".format(self.km.systemName())
        self.region_name = self.km.regionName()
        self.pilot_name = self.km.victim_pilotName()
        self.victimP_zk = __zk_pilot.format(str(self.km.object_victim.character_id))
        self.corp_name = self.km.victim_corpName()
        self.alliance_name = self.km.victim_allianceName()
        __fb = self.km.get_final_blow()
        self.fb_name = self.km.fb_Name(__fb)
        self.fbP_zk = __zk_pilot.format(self.km.fb_pID(__fb))
        self.fb_Corp = self.km.fb_Corp(__fb)
        self.fb_ship = self.km.fb_ship(__fb)
        self.inv_str = self.km.str_attacker_count()
        self.damage_taken = self.km.victim_totalDamage()
        self.isk_lost = self.km.victim_iskLost()
        self.total_involved = str(self.km.get_attacker_count())
        self.min_ago = self.km.str_minutes_ago()

    def __make_header(self):
        __desc = '**{ship_name}** destroyed in **[{system_name}]' \
                 '({system_link})** ({region_name})\n\n' \
                 '***[{pilot_name}]({victimP_zk}) ' \
                 '({corp_name})** lost their **{ship_name}** to **[{fb_name}]({fbP_zk})' \
                 '({fb_corp})** flying in a **{fb_ship}** {inv_str}.*\n\n'\
                 .format(ship_name=self.ship_name, system_name=self.system_name, system_link=self.system_link,
                         region_name=self.region_name, pilot_name=self.pilot_name, victimP_zk=self.victimP_zk,
                         corp_name=self.corp_name, fb_name=self.fb_name,fbP_zk=self.fbP_zk, fb_corp=self.fb_Corp,
                         fb_ship=self.fb_ship,inv_str=self.inv_str)
        self.embed.description = __desc
        self.embed.title = " "
        self.embed.url = self.__zk_kill
        self.embed.set_thumbnail(url="https://imageserver.eveonline.com/Character/{}_64.jpg".format(self.km.victim_pilotID()))
        self.embed.set_image(url="https://imageserver.eveonline.com/Render/{}_128.png".format(str(self.km.object_victim.ship_type_id)))
        self.embed.timestamp = self.km.killmail_time

    def __make_body(self):
        __field_body = "```{Ship:<14}{ship_name}\n" \
                       "{Name:<14}{pilot_name}\n" \
                       "{Corp:<14}{corp_name}\n{Alliance:<14}{alliance_name}\n{Damage_Taken:<14}{damage_taken}\n" \
                       "{Involved:<14}{inv}\n{ISK_Lost:<14}{isk_lost}\n{Time:<14}{min_ago}```**{zk}**" \
                        .format(Ship='Ship:',Name="Name:",Corp="Corp:",Alliance="Alliance:",Damage_Taken="Damage Taken:",
                                Involved="Involved:",ISK_Lost="ISK Lost:",Time="Time:",zk=self.__zk_kill,
                                ship_name=self.ship_name,pilot_name=self.pilot_name,corp_name=self.corp_name,
                                alliance_name=self.alliance_name,damage_taken=self.damage_taken,inv=self.total_involved,
                                isk_lost=self.isk_lost,min_ago=self.min_ago)
        self.embed.add_field(name="**Details**", value=__field_body,inline=False)

    def generate_view(self):
        self.__make_vars()
        self.__make_header()
        self.__make_body()

    def run_filter(self):
        __list_aff = self.filters.object_filter_alliances + self.filters.object_filter_corporations + self.filters.object_filter_characters
        if self.km.filter_victim(self.km.object_victim,filter_list=__list_aff,using_blacklist=self.in_victim_affiliation) is None: #affiliated is victim/loss
            self.__set_loss()
            if self.feed_options.show_mode == enum_kmType.kills_only:
                return False
            if self.feed_options.show_mode == enum_kmType.losses_only or self.feed_options.show_mode == enum_kmType.show_both:
                return True
        else: #km victim is not affiliated/kill
            self.__set_kill()
            if self.feed_options.show_mode == enum_kmType.losses_only:
                return False
            if len(self.km.filter_attackers(self.km.object_attackers,filter_list=__list_aff,using_blacklist=self.in_attackers_affiliation)) > 0:
                return True
            else:
                return False
        return False

    @classmethod
    def feed_specific_row_type(cls):
        return tb_enfeed