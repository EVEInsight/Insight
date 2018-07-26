from .discord_base import *
from ..eve import tb_alliances


class Users(dec_Base.Base, discord_channel_base):
    __tablename__ = 'discord_users'

    user_id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=False)
    user_name = Column(String, default="")

    object_tokens = relationship("Tokens", cascade="delete", uselist=True, back_populates="object_user")

    def __init__(self, object_id):
        self.user_id = object_id

    @classmethod
    def primary_key_row(cls):
        return cls.user_id


from ..filters import *
from ..eve import *
