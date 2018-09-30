from ..enFeed import *


class AllianceTournamentStreamSystem(enFeed):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.show_mode = dbRow.enum_kmType.show_both
            db.add(dbRow.tb_Filter_regions(10000004, self.channel_id, load_fk=False))
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return Linked_Options.opt_basicfeed(self)

    @classmethod
    def get_template_id(cls):
        return 8

    @classmethod
    def get_template_desc(cls):
        return "Alliance Tournament Stream - Displays all losses occurring in the region UUA-F4 for the Alliance Tournament."

    def __str__(self):
        return "Alliance Tournament systems Feed"

    def make_derived_visual(self, visual_class):
        class VisualAllianceTournamentStream(visual_class):
            def internal_list_options(self):
                super(visual_enfeed, self).internal_list_options()
                self.in_system_nonly = internal_options.use_whitelist.value

            def set_frame_color(self):
                self.embed.color = discord.Color(659493)

        return VisualAllianceTournamentStream

    @classmethod
    def is_preconfigured(cls):
        return True
