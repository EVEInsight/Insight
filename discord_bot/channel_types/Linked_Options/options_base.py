from .. import base_object


class Options_Base(base_object.discord_feed_service):

    async def get_option_coroutines(self,required_only=False):
        for i in dir(self):
            if required_only and i.startswith("InsightOptionRequired_"):
                yield getattr(self,i)
            elif not required_only and (i.startswith("InsightOption_") or i.startswith("InsightOptionRequired_")):
                yield getattr(self,i)
            else:
                continue
