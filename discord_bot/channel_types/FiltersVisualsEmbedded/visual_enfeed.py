from .FiltersVisualsEmbedded import *


class visual_enfeed(base_visual):

    def __init__(self, km_row, discord_channel_object, overall_filters, feed_specific_row):
        super(visual_enfeed, self).__init__(km_row, discord_channel_object, overall_filters, feed_specific_row)
        assert isinstance(self.feed_options, tb_enfeed)
        self.is_kill = False

    def make_images(self):
        super().make_images()
        if self.km.object_victim.alliance_id is not None:
            self.__im_victim_corpAli = "https://imageserver.eveonline.com/Alliance/{}_128.png".format\
                (str(self.km.object_victim.alliance_id))
        else:
            self.__im_victim_corpAli = "https://imageserver.eveonline.com/Corporation/{}_128.png".format(
                str(self.km.object_victim.corporation_id))

    def internal_list_options(self):
        super(visual_enfeed, self).internal_list_options()
        self.in_attackers_affiliation = internal_options.use_whitelist.value

    def __set_loss(self):
        self.is_kill = False

    def __set_kill(self):
        self.is_kill = True

    def make_vars(self):
        super(visual_enfeed, self).make_vars()
        self.author_text = "Kill" if self.is_kill else "Loss"
        self.embed.color = discord.Color(65299) if self.is_kill else discord.Color(16711680)

    def make_header(self):
        self.embed.set_author(name=self.author_text, url=self.zk_kill, icon_url=self.__im_victim_corpAli)
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
        self.embed.url = self.zk_kill
        self.embed.set_thumbnail(url="https://imageserver.eveonline.com/Character/{}_64.jpg".format(self.km.victim_pilotID()))
        self.embed.set_image(url="https://imageserver.eveonline.com/Render/{}_128.png".format(str(self.km.object_victim.ship_type_id)))
        self.embed.timestamp = self.km.killmail_time

    def make_body(self):
        __field_body = "```{Ship:<14}{ship_name}\n" \
                       "{Name:<14}{pilot_name}\n" \
                       "{Corp:<14}{corp_name}\n{Alliance:<14}{alliance_name}\n{Damage_Taken:<14}{damage_taken}\n" \
                       "{Involved:<14}{inv}\n{ISK_Lost:<14}{isk_lost}\n{Time:<14}{min_ago}```**{zk}**" \
            .format(Ship='Ship:', Name="Name:", Corp="Corp:", Alliance="Alliance:", Damage_Taken="Damage Taken:",
                    Involved="Involved:", ISK_Lost="ISK Lost:", Time="Time:", zk=self.zk_kill,
                    ship_name=self.ship_name, pilot_name=self.pilot_name, corp_name=self.corp_name,
                    alliance_name=self.alliance_name, damage_taken=self.damage_taken, inv=self.total_involved,
                    isk_lost=self.isk_lost, min_ago=self.min_ago)
        self.embed.add_field(name="**Details**", value=__field_body,inline=False)


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