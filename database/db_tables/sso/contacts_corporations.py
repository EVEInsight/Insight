from .sso_base import *


class Contacts_Corporations(dec_Base.Base, sso_base):
    __tablename__ = 'contacts_corporations'

    token = Column(String, ForeignKey("tokens.refresh_token"), primary_key=True, nullable=False, autoincrement=False)
    owner = Column(Enum(contact_owner), primary_key=True, default=contact_owner.pilot, nullable=False, index=False)
    corporation_id = Column(Integer, ForeignKey("corporations.corporation_id"), primary_key=True, nullable=False,
                            autoincrement=False)
    standing = Column(Float, default=0.0, nullable=False)

    object_token = relationship("Tokens", uselist=False, back_populates="object_contacts_corps")
    object_corp = relationship("Corporations", uselist=False)

    def __init__(self, eve_id: int, owner, standing, service_module):
        self.corporation_id = eve_id
        self.owner = owner
        self.standing = standing
        self.load_fk_objects(service_module)

    def load_fk_objects(self, service_module):
        if self.corporation_id:
            self.object_corp = tb_corporations.get_row(self.corporation_id, service_module)
