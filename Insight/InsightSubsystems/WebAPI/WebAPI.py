from aiohttp import web
from InsightSubsystems.SubsystemBase import SubsystemBase


class WebAPI(SubsystemBase):
    def __init__(self, subsystemloader):
        super().__init__(subsystemloader)

        self.app = web.Application()
        self.app.router.add_get('/', self.home)
        self.app.router.add_get('/ping', self.ping)
        self.runner = web.AppRunner(self.app)
        self.enabled = self.config.get("WEBSERVER_ENABLED")
        self.host = self.config.get("WEBSERVER_INTERFACE")
        self.port = self.config.get("WEBSERVER_PORT")
        self.headers = {"Server": "none"}

    async def home(self, request):
        raise web.HTTPFound("https://eveinsight.net", headers=self.headers)

    async def ping(self, request):
        return web.json_response({"response": "ok"}, headers=self.headers)

    async def start_subsystem(self):
        if self.enabled:
            await super().start_subsystem()
            await self.runner.setup()
            site = web.TCPSite(self.runner, shutdown_timeout=15, host=self.host, port=self.port)
            await site.start()
            print("Webserver is enabled and running at: {}:{}".format(self.host, self.port))

    async def stop_subsystem(self):
        if self.enabled:
            print("Shutting down webserver...")
            await self.runner.cleanup()