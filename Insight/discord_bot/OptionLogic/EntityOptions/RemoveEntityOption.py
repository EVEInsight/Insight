from discord_bot.OptionLogic.EntityOptions.AbstractEntityOption import *
from InsightUtilities import TextLoader
from database.db_tables import tb_Filter_alliances, tb_Filter_corporations, tb_Filter_characters


class RemoveEntityOption(AbstractEntityOption):
    def get_description(self) -> str:
        return "It does something"  # todo implement

    def get_options(self):
        db: Session = self.cfeed.service.get_session()
        options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, self.message)
        options.set_main_header(TextLoader.text_sync("Options.Entity.RemoveEntity_body1"))
        try:
            for pilot in db.query(tb_Filter_characters).filter(
                    tb_Filter_characters.channel_id == self.cfeed.channel_id).all():
                options.add_option(
                    dOpt.option_returns_object(name=pilot.object_item.get_name(), return_object=pilot))
            for corp in db.query(tb_Filter_corporations).filter(
                    tb_Filter_corporations.channel_id == self.cfeed.channel_id).all():
                options.add_option(
                    dOpt.option_returns_object(name=corp.object_item.get_name(), return_object=corp))
            for ali in db.query(tb_Filter_alliances).filter(
                    tb_Filter_alliances.channel_id == self.cfeed.channel_id).all():
                options.add_option(dOpt.option_returns_object(name=ali.object_item.get_name(), return_object=ali))
        except Exception as ex:
            print(ex)
        finally:
            db.close()
            return options

    async def _run_command(self):
        remove_additional = True
        while remove_additional:
            options = await self._executor(self.get_options)
            row = await options()
            await self._delete_row(row)
            await self._reload(self.message)
            remove_add_prompt = dOpt.mapper_return_yes_no(self.cfeed.discord_client, self.message)
            remove_add_prompt.set_main_header(await TextLoader.text_async("Options.Entity.RemoveEntity_body2"))
            remove_additional = await remove_add_prompt()
