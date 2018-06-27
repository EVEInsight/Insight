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

    def generate_view(self):
        fb = self.km.get_final_blow()
        zk_char = "https://zkillboard.com/character/{}/"
        __desc = '**{ship_name}** destroyed in **[{system_name}]' \
                 '({system_link})** ({region_name})\n\n' \
                 '***[{pilot_name}]({victimP_zk}) ' \
                 '({corp_name})** lost their **{ship_name}** to **[{fb_name}]({fbP_zk})' \
                 '({fb_corp})** flying in a **{fb_ship}** {inv_count}.*\n\n'\
                 .format(ship_name=str(self.km.object_victim.object_ship.type_name),
                         system_name=self.km.systemName(),
                         system_link="http://evemaps.dotlan.net/system/{}/".format(self.km.systemName()),
                         region_name=self.km.regionName(),
                         pilot_name=self.km.victim_pilotName(),
                         victimP_zk=zk_char.format(str(self.km.object_victim.character_id)),
                         corp_name=self.km.victim_corpName(),fb_name=self.km.fb_Name(fb),
                         fbP_zk=zk_char.format(self.km.fb_pID(fb)),fb_corp=self.km.fb_Corp(fb),fb_ship=self.km.fb_ship(fb),
                         inv_count=self.km.str_attacker_count())
        self.embed.description = __desc
        self.embed.title = " "
        self.embed.url = self.__zk_kill
        self.embed.set_thumbnail(url="https://imageserver.eveonline.com/Character/{}_64.jpg".format(self.km.victim_pilotID()))
        self.embed.set_image(url="https://imageserver.eveonline.com/Render/{}_128.png".format(str(self.km.object_victim.ship_type_id)))
        self.embed.timestamp = self.km.killmail_time

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