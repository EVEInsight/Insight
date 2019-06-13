from discord_bot.OptionLogic.EntityOptions.AbstractEntityOption import *
from database.db_tables import tb_enfeed
from InsightUtilities import StaticUtil



class MinValueOption(AbstractEntityOption):
    def get_description(self) -> str:
        return "It does something"  # todo implement

    def bound_type(self) -> str:
        return "lower bound/ minimum value"

    def infinite_bound(self):
        return 0.0

    def text_prompt_body(self):
        return "Options.Entity.MinValue_body"

    def text_prompt_footer(self):
        return "Options.Entity.MinValue_footer"

    def set_min(self):
        """set min otherwise set max"""
        return True

    def set_value(self, isk_val):
        db: Session = self.cfeed.service.get_session()
        try:
            row: tb_enfeed = db.query(tb_enfeed).filter(tb_enfeed.channel_id == self.cfeed.channel_id).one()
            if self.set_min():
                row.minValue = isk_val
            else:
                row.maxValue = isk_val
            if row.maxValue < row.minValue:
                raise InsightExc.InsightException(message="The minimum value cannot be greater than the maximum value.")
            db.merge(row)
            db.commit()
        except InsightExc.InsightException as ex:
            raise ex
        except Exception as ex:
            print(ex)
            raise InsightExc.Db.DatabaseError
        finally:
            db.close()

    async def _run_command(self):
        options = dOpt.mapper_return_noOptions(self.cfeed.discord_client, self.message)
        options.set_main_header(TextLoader.text_sync(self.text_prompt_body()))
        options.set_footer_text(TextLoader.text_sync(self.text_prompt_footer()))
        resp = await options()
        val = StaticUtil.str_to_isk(resp)
        if val <= 0:  # set to infinite bound
            val = self.infinite_bound()
        await self._executor(self.set_value, val)
        if val == self.infinite_bound():
            await self.message.channel.send("The ISK bound has been disabled for {}.".format(self.bound_type()))
        else:
            await self.message.channel.send("The ISK bound is now set at: {:,.2f} ISK for {}.".format(val, self.bound_type()))

