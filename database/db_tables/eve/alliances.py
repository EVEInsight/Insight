from .base_objects import *


class Alliances(dec_Base.Base,name_only):
    __tablename__ = 'alliances'

    alliance_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    alliance_name = Column(String,default=None,nullable=True,index=True)

    api_ETag = Column(String,default=None,nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_attackers= relationship("Attackers", uselist=True,back_populates="object_alliance")
    object_loses= relationship("Victims", uselist=True, back_populates="object_alliance")

    def __init__(self, alliance_id: int):
        self.alliance_id = alliance_id

    def get_id(self):
        return self.alliance_id

    def set_name(self, api_name):
        self.alliance_name = api_name

    def get_name(self):
        return self.alliance_name

    @hybrid_property
    def need_name(self):
        return self.alliance_name == None  # and self.api_Last_Modified is not None and self.api_Expires is not None

    @classmethod
    def primary_key_row(cls):
        return cls.alliance_id