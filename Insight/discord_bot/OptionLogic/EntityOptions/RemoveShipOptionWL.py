from Insight.discord_bot.OptionLogic.EntityOptions.RemoveShipOption import RemoveShipOption


class RemoveShipOptionWL(RemoveShipOption):
    def get_description(self) -> str:
        return "It does something"  # todo implement

    def text_remove_body1(self):
        return "Options.Entity.RemoveShipWhitelist_body1"