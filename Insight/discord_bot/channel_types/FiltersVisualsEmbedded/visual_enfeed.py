from .FiltersVisualsEmbedded import *


class visual_enfeed(base_visual):

    def __init__(self, km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object):
        super().__init__(km_row, discord_channel_object, overall_filters, feed_specific_row, feed_object)
        self.is_kill = False

    def internal_list_options(self):
        super().internal_list_options()
        self.in_attackers_affiliation = internal_options.use_whitelist.value

    def make_images(self):
        super().make_images()
        if self.km.object_victim.alliance_id is not None:
            self.im_victim_corpAli = "https://imageserver.eveonline.com/Alliance/{}_128.png".format \
                (str(self.km.object_victim.alliance_id))
        else:
            self.im_victim_corpAli = "https://imageserver.eveonline.com/Corporation/{}_128.png".format(
                str(self.km.object_victim.corporation_id))

    def make_vars(self):
        super().make_vars()
        self.victim_CorpOrAliName = self.km.victim_allianceName()
        if not self.victim_CorpOrAliName:
            self.victim_CorpOrAliName = self.km.victim_corpName()
        self.fb_CorpOrAliName = self.km.fb_Alliance(self.final_blow)
        if not self.fb_CorpOrAliName:
            self.fb_CorpOrAliName = self.km.fb_Corp(self.final_blow)
        self.author_text = "Kill" if self.is_kill else "Loss"

    def set_loss(self):
        self.is_kill = False
        self.color = discord.Color(16711680)

    def set_kill(self):
        self.is_kill = True
        self.color = discord.Color(65299)

    def make_header(self):
        self.embed.set_author(name=self.author_text, url=self.zk_kill, icon_url=self.im_victim_corpAli)
        __desc = '**{ship_name}** destroyed in **[{system_name}]' \
                 '({system_link})**({region_name})\n\n' \
                 '**[{pilot_name}]({victimP_zk})' \
                 '({vAfi})** lost their **{ship_name}** to **[{fb_name}]({fbP_zk})' \
                 '({fbAfi})** flying in a **{fb_ship}** {inv_str}.\n\n' \
            .format(ship_name=self.ship_name, system_name=self.system_name, system_link=self.system_link,
                    region_name=self.region_name, pilot_name=self.pilot_name, victimP_zk=self.victimP_zk,
                    vAfi=self.victim_CorpOrAliName, fb_name=self.fb_name, fbP_zk=self.fbP_zk,
                    fbAfi=self.fb_CorpOrAliName, fb_ship=self.fb_ship, inv_str=self.inv_str)
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
                       "{Involved:<14}{inv}\n{ISK_Lost:<14}{isk_lost}\n{Time:<14}{min_ago}```**[zKill KM]({zk})**" \
            .format(Ship='Ship:', Name="Name:", Corp="Corp:", Alliance="Alliance:", Damage_Taken="Damage Taken:",
                    Involved="Involved:", ISK_Lost="ISK Lost:", Time="Time:", zk=self.zk_kill,
                    ship_name=self.ship_name, pilot_name=self.pilot_name, corp_name=self.corp_name,
                    alliance_name=self.alliance_name, damage_taken=self.damage_taken, inv=self.total_involved,
                    isk_lost=self.isk_lost, min_ago=self.min_ago)
        self.embed.add_field(name="**Details**", value=__field_body,inline=False)

    def run_filter(self):
        tdiff = datetime.datetime.utcnow() - datetime.timedelta(
            hours=3)  # hardcoded entity feed limits to prevent posting month old KMs
        if tdiff >= self.km.killmail_time:
            return False
        if self.feed_options.minValue > self.km.totalValue:
            return False
        if not self.km.filter_loss(self.filters.object_filter_groups,
                                   self.in_victim_ship_group):  # if false/contained in cat blacklist ignore posting
            return False
        __list_systems = self.filters.object_filter_systems + self.filters.object_filter_regions
        match_syst = self.km.filter_system(__list_systems, self.in_system_nonly)
        if match_syst is None:
            return False
        __list_aff = self.filters.object_filter_alliances + self.filters.object_filter_corporations + self.filters.object_filter_characters
        if self.km.filter_victim(self.km.object_victim,filter_list=__list_aff,using_blacklist=self.in_victim_affiliation) is None: #affiliated is victim/loss
            self.set_loss()
            if self.feed_options.show_mode == enum_kmType.kills_only:
                return False
            if self.feed_options.show_mode == enum_kmType.losses_only or self.feed_options.show_mode == enum_kmType.show_both:
                return True
        else: #km victim is not affiliated/kill
            self.set_kill()
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

    @classmethod
    def get_desc(cls):
        return "Full - Detailed killmail overview, pilot and ship images, color sidebar, and zKillboard/Dotlan links. Size: Large"

    @classmethod
    def appearance_options(cls):
        yield cls
        yield VisualEnfeedCompact
        yield VisualEnfeedLinkOnly


from .VisualEnfeedCompact import VisualEnfeedCompact
from .VisualEnfeedLinkOnly import VisualEnfeedLinkOnly
