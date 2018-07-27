from ..enFeed import *


class VisualAllianceTournamentStream(visual_enfeed):
    def internal_list_options(self):
        super(visual_enfeed, self).internal_list_options()
        self.in_system_nonly = internal_options.use_whitelist.value

    def set_frame_color(self):
        self.embed.color = discord.Color(659493)


class AllianceTournamentStreamSystemA(enFeed):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.show_mode = dbRow.enum_kmType.show_both
            db.merge(row)
            db.merge(dbRow.tb_Filter_systems(30000379, self.channel_id))
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return Linked_Options.opt_basicfeed(self)

    def linked_visual(self, km_row):
        return VisualAllianceTournamentStream(km_row, self.channel_discord_object, self.cached_feed_table,
                                              self.cached_feed_specific,
                                              self)

    @classmethod
    def get_template_id(cls):
        return 8

    @classmethod
    def get_template_desc(cls):
        return "AT Stream PE1-R1 - Streams all losses in the Alliance Tournament system PE1-R1."

    def __str__(self):
        return "Alliance Tournament PE1-R1 Feed"


class AllianceTournamentStreamSystemB(enFeed):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.show_mode = dbRow.enum_kmType.show_both
            db.merge(row)
            db.merge(dbRow.tb_Filter_systems(30000381, self.channel_id))
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return Linked_Options.opt_basicfeed(self)

    def linked_visual(self, km_row):
        return VisualAllianceTournamentStream(km_row, self.channel_discord_object, self.cached_feed_table,
                                              self.cached_feed_specific,
                                              self)

    @classmethod
    def get_template_id(cls):
        return 9

    @classmethod
    def get_template_desc(cls):
        return "AT Stream JB-007 - Streams all losses in the Alliance Tournament system JB-007."

    def __str__(self):
        return "Alliance Tournament JB-007 Feed"
