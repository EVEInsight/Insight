from ..enFeed import *


class SuperLosses(enFeed):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.show_mode = dbRow.enum_kmType.show_both
            db.merge(row)
            db.merge(dbRow.tb_Filter_groups(659, self.channel_id))
            db.merge(dbRow.tb_Filter_groups(30, self.channel_id))
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return Linked_Options.opt_basicfeed(self)

    @classmethod
    def get_template_id(cls):
        return 1

    @classmethod
    def get_template_desc(cls):
        return "Super Losses - Displays titan and supercarrier losses."

    def __str__(self):
        return "Super Losses Feed"

    def make_derived_visual(self, visual_class):
        class VisualSuperLosses(visual_class):
            def internal_list_options(self):
                super(visual_enfeed, self).internal_list_options()
                self.in_victim_ship_group = internal_options.use_whitelist.value

            def set_frame_color(self):
                self.embed.color = discord.Color(2640791)

        return VisualSuperLosses

    @classmethod
    def is_preconfigured(cls):
        return True
