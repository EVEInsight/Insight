from .discord_base import *
from ..eve import tb_alliances


class Discord_Tokens(dec_Base.Base, discord_channel_base):
    __tablename__ = 'discord_tokens'

    channel_id = Column(BIGINT, ForeignKey("discord_channels.channel_id"), primary_key=True, nullable=False,
                        autoincrement=False)
    token = Column(String, ForeignKey("tokens.refresh_token"), primary_key=True, nullable=False)

    object_channel = relationship("Channels", uselist=False, back_populates="object_tokens")
    object_token = relationship("Tokens", uselist=False, back_populates="object_channels")

    def __init__(self, channel_id, token):
        self.channel_id = channel_id
        self.token = token

    def get_all_pilot_ids(self):
        if self.object_token.object_contacts_pilots:
            for c in self.object_token.object_contacts_pilots:
                if c.standing > 0.0:
                    yield c.get_id()
        else:
            return None

    def get_all_corp_ids(self):
        if self.object_token.object_contacts_corps:
            for c in self.object_token.object_contacts_corps:
                if c.standing > 0.0:
                    yield c.get_id()
        else:
            return None

    def get_all_alliance_ids(self):
        if self.object_token.object_contacts_alliances:
            for c in self.object_token.object_contacts_alliances:
                if c.standing > 0.0:
                    yield c.get_id()
        else:
            return None

    def __str__(self):
        return str(self.object_token)

    @classmethod
    def primary_key_row(cls):
        return cls.channel_id


from ..filters import *
from ..eve import *
