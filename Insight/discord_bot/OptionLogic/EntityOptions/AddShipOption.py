from Insight.discord_bot.OptionLogic.EntityOptions.AbstractEntityOption import *
from database.db_tables import tb_types, tb_groups, SearchHelper, tb_Filter_types, tb_Filter_groups
from InsightUtilities import StaticUtil


class AddShipOption(AbstractEntityOption):
    def get_description(self) -> str:
        return "It does something"  # todo implement

    def text_location_addship_header(self) -> str:
        return "Options.Entity.AddShipBlacklist_header"

    def make_options(self, s_str):
        db: Session = self.cfeed.service.get_session()
        results = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, self.message)
        results.set_main_header(TextLoader.text_sync(self.text_location_addship_header()))
        try:
            search_items = SearchHelper.search_type_group_is_ship(db, s_str)
            for r in StaticUtil.filter_type(search_items, tb_types):
                results.add_unique_header_row("Types")
                res_name = "ID: {} Name: {}".format(str(r.get_id()), r.get_name())
                f = tb_Filter_types(r.get_id(), self.cID, False)
                results.add_option(dOpt.option_returns_object(name=res_name, return_object=f))
            for r in StaticUtil.filter_type(search_items, tb_groups):
                results.add_unique_header_row("Groups")
                res_name = "ID: {} Name: {}".format(str(r.get_id()), r.get_name())
                f = tb_Filter_groups(r.get_id(), self.cID, False)
                results.add_option(dOpt.option_returns_object(name=res_name, return_object=f))
            results.add_header_row("Additional Options")
            results.add_option(dOpt.option_returns_object("Search again", return_object=None))
            return results
        except Exception as ex:
            raise ex
        finally:
            db.close()

    async def _run_command(self):
        search = dOpt.mapper_return_noOptions(self.cfeed.discord_client, self.message)
        search.set_main_header("Enter the name or ID of a ship/npc type/group to search for.")
        search.set_footer_text("Enter a name or ID. Note: partial names are accepted: ")
        selected_row = None
        while selected_row is None:
            search_name = await search()
            found_results = await self._executor(self.make_options, search_name)
            selected_row = await found_results()
        await self._save_row(selected_row)
