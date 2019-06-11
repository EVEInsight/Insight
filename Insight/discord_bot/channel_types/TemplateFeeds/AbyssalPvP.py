from ..enFeed import *


class OptionsAbyssalPvP(Linked_Options.opt_enfeed):
    def yield_options(self):
        yield (self.InsightOption_minValue, True)
        yield (self.InsightOption_maxValue, False)
        yield from super(Linked_Options.opt_enfeed, self).yield_options()


class AbyssalPvP(enFeed):
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
            raise ex
        finally:
            db.close()

    def get_linked_options(self):
        return OptionsAbyssalPvP(self)

    @classmethod
    def get_template_id(cls):
        return 13

    @classmethod
    def get_template_desc(cls):
        return "Abyssal PvP (Beta) - Displays PvP losses in Abyssal space."

    def __str__(self):
        return "Abyssal PvP"

    def make_derived_visual(self, visual_class):
        class VisualAbyssalPvP(visual_class):
            def internal_list_options(self):
                super(visual_enfeed, self).internal_list_options()
                self.in_system_nonly = internal_options.use_whitelist.value

            def run_filter(self):
                if (datetime.datetime.utcnow() - self.max_delta()) >= self.km.killmail_time:
                    return False
                if self.feed_options.minValue > self.km.totalValue:
                    return False
                if self.km.is_npc():
                    return False
                if self.km.filter_system(self.filters.object_filter_regions, self.in_system_nonly) is None:
                    return False
                self.set_kill()
                return True

            def set_frame_color(self):
                self.embed.color = discord.Color(2640791)

            def max_delta(self):
                return datetime.timedelta(hours=3)

        return VisualAbyssalPvP

    @classmethod
    def is_preconfigured(cls):
        return True
