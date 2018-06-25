from .. import base_object as channel_type_base


class Options_Base(channel_type_base.discord_feed_service):
    async def all_options(self):
        for i in dir(self):
            if i.startswith("InsightOption_") or i.startswith("InsightOptionRequired_"):
                test = getattr(self,i)
                yield test

    async def all_options_required(self):
        for i in dir(self):
            if i.startswith("InsightOptionRequired_"):
                test = getattr(self,i)
                yield test