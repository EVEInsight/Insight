from .discord_base import *
from . import discord_channels


class km_type_mode(enum.Enum):
    losses_only = 'losses_only'
    kills_only = 'kills_only'
    show_both = 'show_both'


class EnFeed(dec_Base.Base,discord_channel_base):
    __tablename__ = 'discord_enFeed'

    channel_id = Column(BIGINT,ForeignKey("discord_channels.channel_id"),primary_key=True,nullable=False,autoincrement=False)
    template_id = Column(Integer, default=0, nullable=False)
    show_mode = Column(Enum(km_type_mode),default=km_type_mode.show_both,nullable=False)
    object_channel = relationship("Channels", uselist=False, back_populates="object_enFeed",lazy="joined")

    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.load_fk_objects()

    def load_fk_objects(self):
        if self.channel_id is not None:
            self.object_channel = discord_channels.Channels(self.channel_id)

    @classmethod
    def primary_key_row(cls):
        return cls.channel_id