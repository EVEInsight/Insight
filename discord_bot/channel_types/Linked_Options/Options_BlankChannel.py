from . import options_base
from .. import nofeed_text


class Options_BlankChannel(options_base.Options_Base):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, nofeed_text.discord_text_nofeed_exist)
        super().__init__(insight_channel)
