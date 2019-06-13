from discord_bot.OptionLogic.EntityOptions.AbstractEntityOption import *


class RemoveShipOption(AbstractEntityOption):
    def get_description(self) -> str:
        return "It does something"  # todo implement

    def text_remove_body1(self):
        return "Options.Entity.RemoveShipBlacklist_body1"

    def make_options(self):
        db: Session = self.cfeed.service.get_session()
        remove = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, self.message)
        remove.set_main_header(TextLoader.text_sync(self.text_remove_body1()))
        try:
            for i in self._get_row().object_filter_types:
                remove.add_unique_header_row("Types")
                n_str = "{}".format(i.object_item.get_name())
                remove.add_option(dOpt.option_returns_object(name=n_str, return_object=i))
            for i in self._get_row().object_filter_groups:
                remove.add_unique_header_row("Groups")
                n_str = "{}".format(i.object_item.get_name())
                remove.add_option(dOpt.option_returns_object(name=n_str, return_object=i))
            return remove
        except Exception as ex:
            print(ex)
            raise InsightExc.Db.DatabaseError
        finally:
            db.close()

    async def _run_command(self):
        rem_options = await self._executor(self.make_options)
        row = await rem_options()
        await self._delete_row(row)
