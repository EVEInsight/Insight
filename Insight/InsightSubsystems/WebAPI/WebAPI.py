from aiohttp import web
from InsightSubsystems.SubsystemBase import SubsystemBase


class WebAPI(SubsystemBase):
    def __init__(self, subsystemloader):
        super().__init__(subsystemloader)

        self.app = web.Application()
        self.app.router.add_get('/', self.home)
        self.app.router.add_get('/ping', self.ping)
        self.app.router.add_get('/callback', self.callback)
        self.runner = web.AppRunner(self.app)
        self.enabled = self.config.get("WEBSERVER_ENABLED")
        self.host = self.config.get("WEBSERVER_INTERFACE")
        self.port = self.config.get("WEBSERVER_PORT")
        self.callback_redirect_success = self.config.get("CALLBACK_REDIRECT_SUCCESS")
        self.headers = {"Server": "none"}
        self.sso = self.service.sso

    async def home(self, request):
        raise web.HTTPFound("https://eveinsight.net", headers=self.headers)

    async def ping(self, request):
        return web.json_response({"response": "ok"}, headers=self.headers)

    async def callback(self, request):
        if request.content_type != "application/octet-stream":
            raise web.HTTPBadRequest(text="Bad Content-Type, expected application/octet-stream", headers=self.headers)
        else:
            code = request.query.get("code", None)
            state = request.query.get("state", None)
            if not state:
                raise web.HTTPBadRequest(text="Missing 'state' parameter",
                                         headers=self.headers)
            if not code:
                raise web.HTTPBadRequest(text="Missing 'code' parameter",
                                         headers=self.headers)

            if not await self.sso.validate_state(state):
                raise web.HTTPNotFound(text="Invalid 'state' parameter. There are no states open with the provided "
                                            "state code.\nIt is likely that the SSO link provided expired. "
                                            "Please run the !sync command again.", headers=self.headers)
            else:
                await self.sso.set_state_code(state_str=state, state_code=code)
                if self.callback_redirect_success:
                    raise web.HTTPFound(self.callback_redirect_success, headers=self.headers)
                else:
                    return web.Response(text="EVE SSO login success. Your token is now linked to your "
                                             "Discord user and you may close this window. \nYour EVE Insight admin "
                                             "can change this page by setting the 'CALLBACK_REDIRECT_SUCCESS' variable "
                                             "to redirect to a different landing page on successful SSO callback.",
                                        headers=self.headers)

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