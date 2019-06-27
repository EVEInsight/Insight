from ..enFeed import *
from discord_bot.OptionLogic.EntityOptions import *


class OptionsShipLosses(Linked_Options.opt_enfeed):
    def yield_options(self):
        yield (AddShipOptionWL(self.cfeed).run_message, True)
        yield (RemoveShipOptionWL(self.cfeed).run_message, False)
        yield (self.InsightOption_minValue, False)
        yield (self.InsightOption_maxValue, False)
        yield from super(Linked_Options.opt_enfeed, self).yield_options()


class ShipLosses(enFeed):
    def get_linked_options(self):
        return OptionsShipLosses(self)

    @classmethod
    def get_template_id(cls):
        return 14

    @classmethod
    def get_template_desc(cls):
        return "Ship Losses - null"  # todo desc

    def __str__(self):
        return "Ship Losses Feed"

    def make_derived_visual(self, visual_class):
        class VisualShipLosses(visual_class):
            def internal_list_options(self):
                super(visual_enfeed, self).internal_list_options()
                self.in_victim_ship_group = internal_options.use_whitelist.value

            def set_frame_color(self):
                self.embed.color = discord.Color(2640791)

            def max_delta(self):
                return datetime.timedelta(days=7)

        return VisualShipLosses

    @classmethod
    def is_preconfigured(cls):
        return True
