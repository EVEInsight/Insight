from database.tables.discord_base import *
from database.tables import *


class CapRadar(Base,discord_channel_base):
    __tablename__ = 'capRadar'

    channel_id = Column(BIGINT,ForeignKey("channels.channel_id"),primary_key=True,nullable=False,autoincrement=False)
    object_channel = relationship("Channels", uselist=False, back_populates="object_capRadars",lazy="joined")

    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.load_fk_objects()

    def load_fk_objects(self):
        if self.channel_id is not None:
            self.object_channel = tb_channels(self.channel_id)

    @classmethod
    def primary_key_row(cls):
        return cls.channel_id