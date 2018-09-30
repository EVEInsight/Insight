from .base_filter import *
from ..eve import systems


class Filter_systems(dec_Base.Base,filter_base):
    __tablename__ = 'filter_systems'

    channel_id = Column(BIGINT,ForeignKey("discord_channels.channel_id"),primary_key=True,nullable=False,autoincrement=False)
    filter_id = Column(Integer, ForeignKey("systems.system_id"),primary_key=True, nullable=False,autoincrement=False)
    list_type = Column(Enum(listTypeEnum), primary_key=True, default=listTypeEnum.nolist, nullable=False)
    min = Column(Float,default=None,nullable=True)
    max = Column(Float,default=None,nullable=True)
    mention = Column(Enum(mention_method),default=mention_method.noMention,nullable=False)

    object_channel = relationship("Channels",uselist=False,back_populates="object_filter_systems")
    object_item = relationship("Systems",uselist=False,lazy="joined")

    def __init__(self, eve_id: int, discord_channel_id, load_fk=True):
        self.filter_id = eve_id
        self.channel_id = discord_channel_id
        if load_fk:
            self.load_fk_objects()

    def load_fk_objects(self):
        self.object_channel = discord_channels.Channels(self.channel_id) if self.channel_id else None
        self.object_item = systems.Systems(self.filter_id) if self.filter_id else None