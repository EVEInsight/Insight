from .discord_base import *
from . import discord_servers


class Prefixes(dec_Base.Base, discord_channel_base):
    __tablename__ = 'discord_prefixes'

    server_id = Column(BIGINT, ForeignKey("discord_servers.server_id"), primary_key=True, nullable=False,
                        autoincrement=False)
    prefix = Column(String, primary_key=True, nullable=False)

    object_server = relationship("Servers", uselist=False, back_populates="object_prefixes")

    def __init__(self, server_id: int, prefix: str, load_fk=True):
        self.server_id = server_id
        self.prefix = prefix
        if load_fk:
            self.load_fk_objects()

    def load_fk_objects(self):
        self.object_server = discord_servers.Servers(self.server_id) if self.server_id else None

    @classmethod
    def primary_key_row(cls):
        return cls.server_id
