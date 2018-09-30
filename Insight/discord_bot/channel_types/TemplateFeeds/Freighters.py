from ..enFeed import *


class OptionsFreighters(Linked_Options.opt_enfeed):
    def yield_options(self):
        yield (self.InsightOption_minValue, False)
        yield from super(Linked_Options.opt_enfeed, self).yield_options()


class Freighters(enFeed):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.show_mode = dbRow.enum_kmType.show_both
            for r in db.query(dbRow.tb_systems).filter(dbRow.tb_systems.security_status >= .45).all():
                db.add(dbRow.tb_Filter_systems(r.system_id, self.channel_id, load_fk=False))
            db.add(dbRow.tb_Filter_groups(513, self.channel_id, load_fk=False))
            db.add(dbRow.tb_Filter_groups(902, self.channel_id, load_fk=False))
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return OptionsFreighters(self)

    @classmethod
    def get_template_id(cls):
        return 7

    @classmethod
    def get_template_desc(cls):
        return "Freighter Ganks - Displays freighter and jump freighter losses in high-security space."

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

    @classmethod
    def is_preconfigured(cls):
        return True
