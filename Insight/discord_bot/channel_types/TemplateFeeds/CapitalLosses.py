from ..enFeed import *


class OptionsCapitalLosses(Linked_Options.opt_enfeed):
    def yield_options(self):
        yield (self.InsightOption_minValue, False)
        yield from super(Linked_Options.opt_enfeed, self).yield_options()


class CapitalLosses(enFeed):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.show_mode = dbRow.enum_kmType.show_both
            db.add(dbRow.tb_Filter_groups(659, self.channel_id, load_fk=False))  # sc
            db.add(dbRow.tb_Filter_groups(30, self.channel_id, load_fk=False))  # titan
            db.add(dbRow.tb_Filter_groups(547, self.channel_id, load_fk=False))  # carrier
            db.add(dbRow.tb_Filter_groups(485, self.channel_id, load_fk=False))  # dread
            db.add(dbRow.tb_Filter_groups(1538, self.channel_id, load_fk=False))  # fax
            db.add(dbRow.tb_Filter_groups(902, self.channel_id, load_fk=False))  # jf
            db.add(dbRow.tb_Filter_groups(883, self.channel_id, load_fk=False))  # rorq
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return OptionsCapitalLosses(self)

    @classmethod
    def get_template_id(cls):
        return 9

    @classmethod
    def get_template_desc(cls):
        return "Capital Losses - Displays titan, supercarrier, carrier, dread, FAX, JF, and Rorqual losses."

    def __str__(self):
        return "Capital Losses Feed"

    def make_derived_visual(self, visual_class):
        class VisualCapitalLosses(visual_class):
            def internal_list_options(self):
                super(visual_enfeed, self).internal_list_options()
                self.in_victim_ship_group = internal_options.use_whitelist.value

            def set_frame_color(self):
                self.embed.color = discord.Color(2640791)

        return VisualCapitalLosses

    @classmethod
    def is_preconfigured(cls):
        return True
