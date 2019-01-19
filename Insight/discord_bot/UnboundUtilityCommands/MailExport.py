from .UnboundCommandBase import *
from database.db_tables.eve import tb_kills
import json
import os
from functools import partial


class MailExport(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.cLock = asyncio.Lock(loop=self.client.loop)

    def command_description(self):
        return "Mail Export - Export a list of killmail ids to json file objects in the project 'mails' directory."

    def export_ids(self, response_str):
        error_input = []
        ok_ids = []
        os.makedirs("mails", exist_ok=True)
        db = self.service.get_session()
        for i in response_str.split():
            try:
                try:
                    km_id = int(i)
                    row = tb_kills.get_row({"killID": km_id}, self.service)
                    if isinstance(row, tb_kills):
                        with open(os.path.join("mails", "{}.json".format(km_id)), 'w+') as f:
                            json.dump(row.to_jsonDictionary(), f)
                        ok_ids.append(i)
                        continue
                    error_input.append(i)
                except ValueError:
                    error_input.append(i)
            except Exception as ex:
                error_input.append(i)
                print(ex)
            finally:
                db.close()
        response_str = "Output {} mails to the 'mails' directory\n\n".format(len(ok_ids))
        response_str += "Errors occurred on the following inputs:\n\n"
        for e in error_input:
            response_str += "{}\n".format(e)
        return response_str

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        async with self.cLock:
            options = dOpt.mapper_return_noOptions(self.client, d_message)
            options.set_main_header("Copy and paste mail ids separated by space/newlines.")
            resp: str = await options()
            status_message = await self.client.loop.run_in_executor(None, partial(self.export_ids, resp))
            await d_message.channel.send(status_message)
