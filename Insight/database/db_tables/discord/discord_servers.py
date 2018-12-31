from .discord_base import *


class Servers(dec_Base.Base, discord_channel_base):
    __tablename__ = 'discord_servers'

    server_id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=False)
    server_name = Column(String, default="", nullable=False)

    object_prefixes = relationship("Prefixes", uselist=True, cascade="delete", back_populates="object_server")

    def __init__(self, server_id: int):
        self.server_id = server_id

    @classmethod
    def primary_key_row(cls):
        return cls.server_id
