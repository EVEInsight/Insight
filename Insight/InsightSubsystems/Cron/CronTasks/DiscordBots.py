from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask
import aiohttp
import asyncio
import json


class DiscordBots(AbstractCronTask):
    def __init__(self, cron_manager):
        super().__init__(cron_manager)
        self.api_token = self.config.get("DISCORDBOTS_APIKEY")
        self.db_url = "https://discordbots.org/api/bots/{}/stats".format(str(self.client.user.id))
        self.db_headers = {"Content-Type": "application/json", "Authorization": str(self.api_token),
                           **self.service.get_headers()}

    def loop_iteration(self) -> int:
        return 900

    def run_at_intervals(self) -> bool:
        return False

    async def _run_task(self):
        if self.api_token:
            async with aiohttp.ClientSession(headers=self.db_headers) as client:
                try:
                    payload = {"server_count": len(self.client.guilds)}
                    async with client.post(url=self.db_url, data=json.dumps(payload), timeout=45) as r:
                        if r.status == 200:
                            pass
                        elif r.status == 401:
                            print('Error 401 for DiscordBots API. DiscordBots posting will now stop.')
                            self.api_token = None
                        else:
                            print('Error: {} - when posting to DiscordBots API'.format(r.status))
                except asyncio.TimeoutError as ex:
                    print('DiscordBots API timeout.')
                    raise ex
                except Exception as ex:
                    raise ex
