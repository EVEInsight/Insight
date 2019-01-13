from ..enFeed import *


class OptionsSoloNPC(Linked_Options.opt_enfeed):
    def yield_options(self):
        yield (self.InsightOption_minValue, True)
        yield from super(Linked_Options.opt_enfeed, self).yield_options()


class AngryNPC(enFeed):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.show_mode = dbRow.enum_kmType.show_both
            db.add(dbRow.tb_Filter_categories(6, self.channel_id, load_fk=False))  # ships
            db.add(dbRow.tb_Filter_categories(87, self.channel_id, load_fk=False))  # fighters
            db.add(dbRow.tb_Filter_categories(23, self.channel_id, load_fk=False))  # pos
            db.add(dbRow.tb_Filter_categories(66, self.channel_id, load_fk=False))  # citadel items
            db.add(dbRow.tb_Filter_groups(1657, self.channel_id, load_fk=False))  # citadel
            db.commit()
        except Exception as ex:
            print(ex)
            raise ex
        finally:
            db.close()

    def get_linked_options(self):
        return OptionsSoloNPC(self)

    @classmethod
    def get_template_id(cls):
        return 12

    @classmethod
    def get_template_desc(cls):
        return "Angry NPCs (Beta) - Displays pilot losses soloed by NPC ships."

    def __str__(self):
        return "NPC Killboard"

    def make_derived_visual(self, visual_class):
        class VisualSoloNPC(visual_class):
            def internal_list_options(self):
                super(visual_enfeed, self).internal_list_options()
                self.in_attackers_ships_category = internal_options.use_blacklist.value

            def run_filter(self):
                if (datetime.datetime.utcnow() - self.max_delta()) >= self.km.killmail_time:
                    return False
                if self.feed_options.minValue > self.km.totalValue:
                    return False
                filter_crit = self.filters.object_filter_categories + self.filters.object_filter_groups
                tracked_ships = self.km.filter_attackers(self.km.object_attackers, filter_crit, self.in_attackers_ships_category)
                if len(tracked_ships) != len(self.km.object_attackers):
                    return False
                self.set_kill()
                return True

            def set_frame_color(self):
                self.embed.color = discord.Color(2640791)

            def max_delta(self):
                return datetime.timedelta(hours=3)

        return VisualSoloNPC

    @classmethod
    def is_preconfigured(cls):
        return True
