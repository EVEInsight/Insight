from discord_bot.OptionLogic.EntityOptions.AbstractEntityOption import *
from InsightUtilities import TextLoader
from database.db_tables import id_resolver, SearchHelper, tb_alliances, tb_corporations, tb_characters


class AddEntityOption(AbstractEntityOption):
    def get_description(self) -> str:
        return "It does something"  # todo implement

    def header_make(self, row_list: List[tb_alliances], header_text, options):
        if len(row_list) > 0:
            options.add_header_row(header_text)
            for i in row_list:
                options.add_option(dOpt.option_returns_object(name=i.get_name(), return_object=i))

    def make_options(self, search_str) -> dOpt.mapper_index:
        options = dOpt.mapper_index_withAdditional(self.cfeed.discord_client, self.message)
        options.set_main_header(TextLoader.text_sync("Options.Entity.AddEntity_body2"))
        db: Session = self.cfeed.service.get_session()
        try:
            self.header_make(SearchHelper.search(db, tb_alliances, tb_alliances.alliance_name, search_str), "Alliances",
                             options)
            self.header_make(SearchHelper.search(db, tb_corporations, tb_corporations.corporation_name, search_str),
                        "Corporations", options)
            self.header_make(SearchHelper.search(db, tb_characters, tb_characters.character_name, search_str), "Pilots",
                             options)
            options.add_header_row("Additional Options")
            options.add_option(dOpt.option_returns_object("Search again", return_object=None))
            return options
        except Exception as ex:
            raise ex
        finally:
            db.close()

    async def _run_command(self):
        search = dOpt.mapper_return_noOptions(self.cfeed.discord_client, self.message)
        search.set_main_header(await TextLoader.text_async("Options.Entity.AddEntity_body1"))
        search.set_footer_text(await TextLoader.text_async("Options.Entity.AddEntity_footer1"))
        selected_option = None
        while selected_option is None:
            search_name = await search()
            if len(search_name) <= 2:
                raise InsightExc.userInput.ShortSearchCriteria(min_length=3)
            await self._executor(id_resolver.api_mass_id_resolve,self.cfeed.service, search_name) #lookup name from eve api first and add to db
            found_results = await self._executor(self.make_options, search_name)
            selected_option = await found_results()
        await self._executor(tb_channels.commit_list_entry, selected_option, self.cfeed.channel_id, self.cfeed.service)
