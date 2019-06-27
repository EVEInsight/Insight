from discord_bot.OptionLogic.EntityOptions.AbstractEntityOption import *
from database.db_tables import tb_Filter_groups


class SetTrackPodsOption(AbstractEntityOption):
    def get_description(self) -> str:
        return "It does something"  # todo implement

    def pod_group_ids(self):
        yield 29

    def set_mode(self, track_pods):
        db: Session = self.cfeed.service.get_session()
        try:
            if not track_pods:
                for i in self.pod_group_ids():
                    row: tb_Filter_groups = tb_Filter_groups.get_row(self.cfeed.channel_id, i, self.cfeed.service)
                    db.merge(row)
                db.commit()
            else:
                for i in self.pod_group_ids():
                    tb_Filter_groups.get_remove(self.cfeed.channel_id, i, self.cfeed.service)
                db.commit()
        except Exception as ex:
            print(ex)
            raise InsightExc.Db.DatabaseError
        finally:
            db.close()

    async def _run_command(self):
        options = dOpt.mapper_return_yes_no(self.cfeed.discord_client, self.message)
        options.set_main_header(await TextLoader.text_async("Options.Entity..SetTrackPods_Body1"))
        resp = await options()
        await self._executor(self.set_mode, resp)
