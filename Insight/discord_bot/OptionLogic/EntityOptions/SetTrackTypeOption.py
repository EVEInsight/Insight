from discord_bot.OptionLogic.EntityOptions.AbstractEntityOption import *
from database.db_tables import tb_enfeed, enum_kmType


class SetTrackTypOption(AbstractEntityOption):
    def get_description(self) -> str:
        return "It does something"  # todo implement

    def set_mode(self, option):
        db: Session = self.cfeed.service.get_session()
        try:
            row: tb_enfeed = db.query(tb_enfeed).filter(tb_enfeed.channel_id == self.cfeed.channel_id).one()
            row.show_mode = option
            db.merge(row)
            db.commit()
        except Exception as ex:
            print(ex)
            raise InsightExc.Db.DatabaseError
        finally:
            db.close()

    async def _run_command(self):
        options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, self.message)
        options.set_main_header(await TextLoader.text_async("Options.Entity.SetTrackType_body1"))
        options.add_option(dOpt.option_returns_object(
            name=await TextLoader.text_async("Options.Entity.SetTrackType_opt1"),
            return_object=enum_kmType.show_both))
        options.add_option(dOpt.option_returns_object(
            name=await TextLoader.text_async("Options.Entity.SetTrackType_opt2"),
            return_object=enum_kmType.kills_only))
        options.add_option(dOpt.option_returns_object(
            name=await TextLoader.text_async("Options.Entity.SetTrackType_opt3"),
            return_object=enum_kmType.losses_only))
        selection_option = await options()
        await self._executor(self.set_mode, selection_option)
