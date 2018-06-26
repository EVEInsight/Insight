from . import Base_Feed


class Options_CapRadar(Base_Feed.base_activefeed):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, capRadar.capRadar)
        super().__init__(insight_channel)

from .. import capRadar
