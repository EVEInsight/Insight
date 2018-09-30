from ..enFeed import *


class OptionsAbyssalLosses(Linked_Options.opt_enfeed):
    def yield_options(self):
        yield (self.InsightOption_minValue, False)
        yield from super(Linked_Options.opt_enfeed, self).yield_options()


class AbyssalLosses(enFeed):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.show_mode = dbRow.enum_kmType.show_both
            for r in db.query(dbRow.tb_regions).filter(dbRow.tb_regions.region_id >= 12000000,
                                                       dbRow.tb_regions.region_id < 13000000).all():
                db.add(dbRow.tb_Filter_regions(r.region_id, self.channel_id, load_fk=False))
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return OptionsAbyssalLosses(self)

    @classmethod
    def get_template_id(cls):
        return 2

    @classmethod
    def get_template_desc(cls):
        return "Abyssal Losses - Displays losses occurring in Abyssal space."

    def __str__(self):
        return "Abyssal Feed"

    def make_derived_visual(self, visual_class):
        class VisualAbyssalLosses(visual_class):
            def internal_list_options(self):
                super(visual_enfeed, self).internal_list_options()
                self.in_system_nonly = internal_options.use_whitelist.value

            def set_frame_color(self):
                self.embed.color = discord.Color(659493)

        return VisualAbyssalLosses

    @classmethod
    def is_preconfigured(cls):
        return True