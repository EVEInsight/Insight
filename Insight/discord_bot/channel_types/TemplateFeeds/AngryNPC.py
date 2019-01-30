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
            def run_filter(self):
                if (datetime.datetime.utcnow() - self.max_delta()) >= self.km.killmail_time:
                    return False
                if self.feed_options.minValue > self.km.totalValue:
                    return False
                if not self.km.is_npc():
                    return False
                if self.km.get_alive_nonnpc_count(self.km.object_attackers) > 0:
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
