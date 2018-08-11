from ..enFeed import *


class Freighters(enFeed):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.show_mode = dbRow.enum_kmType.show_both
            db.merge(row)
            for r in db.query(dbRow.tb_systems).filter(dbRow.tb_systems.security_status >= .45).all():
                db.merge(dbRow.tb_Filter_systems(r.system_id, self.channel_id))
            db.merge(dbRow.tb_Filter_groups(513, self.channel_id))
            db.merge(dbRow.tb_Filter_groups(902, self.channel_id))
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return Linked_Options.opt_basicfeed(self)

    @classmethod
    def get_template_id(cls):
        return 7

    @classmethod
    def get_template_desc(cls):
        return "Freighter Ganks - Displays all freighters and jump freighters destroyed in high-security space."

    def __str__(self):
        return "Freighter Ganks Feed"

    def make_derived_visual(self, visual_class):
        class VisualFreighters(visual_class):
            def internal_list_options(self):
                super(visual_enfeed, self).internal_list_options()
                self.in_victim_ship_group = internal_options.use_whitelist.value
                self.in_system_nonly = internal_options.use_whitelist.value

            def set_frame_color(self):
                self.embed.color = discord.Color(5857901)

        return VisualFreighters
