from .sso_base import *


class Contacts_Alliances(dec_Base.Base, sso_base):
    __tablename__ = 'contacts_alliances'

    token = Column(String, ForeignKey("tokens.token_id"), primary_key=True, nullable=False)
    owner = Column(Enum(contact_owner), primary_key=True, default=contact_owner.pilot, nullable=False, index=False)
    alliance_id = Column(Integer, ForeignKey("alliances.alliance_id"), primary_key=True, nullable=False,
                         autoincrement=False)
    standing = Column(Float, default=0.0, nullable=False)

    object_token = relationship("Tokens", uselist=False, back_populates="object_contacts_alliances")
    object_alliance = relationship("Alliances", uselist=False)

    def __init__(self, eve_id: int, owner, standing, service_module):
        self.alliance_id = eve_id
        self.owner = owner
        self.standing = standing
        self.load_fk_objects(service_module)

    def load_fk_objects(self, service_module):
        if self.alliance_id:
            self.object_alliance = tb_alliances.get_row(self.alliance_id, service_module)

    def get_id(self):
        return self.alliance_id
