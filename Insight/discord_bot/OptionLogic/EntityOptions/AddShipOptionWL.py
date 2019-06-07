from Insight.discord_bot.OptionLogic.EntityOptions.AddShipOption import AddShipOption


class AddShipOptionWL(AddShipOption):
    def get_description(self) -> str:
        return "It does something"  # todo implement

    def text_prompt1_body(self):
        return "Options.Entity.AddShipWhitelist_body1"

    def text_prompt2_body(self):
        return "Options.Entity.AddShipWhitelist_body2"
