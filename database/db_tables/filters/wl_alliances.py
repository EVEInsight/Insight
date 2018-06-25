from .base_filter import *


class WL_alliances(dec_Base.Base,filter_base):
    __tablename__ = 'wl_alliances'

    channel_id = Column(BIGINT,ForeignKey("channels.channel_id"),primary_key=True,nullable=False,autoincrement=False)
    filter_id = Column(Integer, ForeignKey("alliances.alliance_id"),primary_key=True, nullable=False,autoincrement=False)
    min = Column(Float,default=None,nullable=True)
    max = Column(Float,default=None,nullable=True)
    mention = Column(Enum(mention_method),default=mention_method.noMention,nullable=False)

    object_channel = relationship("Channels",uselist=False,back_populates="object_wl_alliances")
    object_item = relationship("Alliances",uselist=False,lazy="joined")

    def __init__(self, eve_id: int, discord_channel_id: int):
        self.filter_id = eve_id
        self.channel_id = discord_channel_id