from ..enFeed import *


class OptionsBigKills(Linked_Options.opt_enfeed):
    def yield_options(self):
        yield (self.InsightOption_minValue, True)
        yield from super(Linked_Options.opt_enfeed, self).yield_options()


class BigKills(enFeed):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.show_mode = dbRow.enum_kmType.show_both
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return OptionsBigKills(self)

    @classmethod
    def get_template_id(cls):
        return 11

    @classmethod
    def get_template_desc(cls):
        return "Big Kills - Displays expensive kills above a customized minimum ISK value."

    def __str__(self):
        return "Big Kills Feed"

    def make_derived_visual(self, visual_class):
        class VisualBigKills(visual_class):
            def internal_list_options(self):
                super(visual_enfeed, self).internal_list_options()

            def set_frame_color(self):
                self.embed.color = discord.Color(659493)

        return VisualBigKills

    @classmethod
    def is_preconfigured(cls):
        return True
