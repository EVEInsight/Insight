from .sso_base import *


class Contacts_Characters(dec_Base.Base, sso_base):
    __tablename__ = 'contacts_characters'

    token = Column(String, ForeignKey("tokens.token_id"), primary_key=True, nullable=False, autoincrement=False)
    owner = Column(Enum(contact_owner), primary_key=True, default=contact_owner.pilot, nullable=False, index=False)
    character_id = Column(Integer, ForeignKey("characters.character_id"), primary_key=True, nullable=False,
                          autoincrement=False)
    standing = Column(Float, default=0.0, nullable=False)

    object_token = relationship("Tokens", uselist=False, back_populates="object_contacts_pilots")
    object_pilot = relationship("Characters", uselist=False)

    def __init__(self, eve_id: int, owner, standing, service_module):
        self.character_id = eve_id
        self.owner = owner
        self.standing = standing
        self.load_fk_objects(service_module)

    def load_fk_objects(self, service_module):
        if self.character_id:
            self.object_pilot = tb_characters.get_row(self.character_id, service_module)

    def get_id(self):
        return self.character_id
