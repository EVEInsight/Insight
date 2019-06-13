from discord_bot.OptionLogic.EntityOptions.MinValueOption import MinValueOption


class MaxValueOption(MinValueOption):
    def bound_type(self) -> str:
        return "upper bound/ maximum value"

    def infinite_bound(self):
        return 1e60

    def text_prompt_body(self):
        return "Options.Entity.MaxValue_body"

    def text_prompt_footer(self):
        return "Options.Entity.MaxValue_footer"

    def set_min(self):
        return False

