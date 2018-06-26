from .base_objects import *


class Corporations(dec_Base.Base,name_only):
    __tablename__ = 'corporations'

    corporation_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    corporation_name = Column(String,default=None,nullable=True,index=True)

    api_ETag = Column(String,default=None,nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_attackers = relationship("Attackers", uselist=True,back_populates="object_corp")
    object_loses = relationship("Victims", uselist=True, back_populates="object_corp")

    def __init__(self, corp_id: int):
        self.corporation_id = corp_id

    def get_id(self):
        return self.corporation_id

    def set_name(self, api_name):
        self.corporation_name = api_name

    def get_name(self):
        return self.corporation_name

    @hybrid_property
    def need_name(self):
        return self.corporation_name == None  # and self.api_Last_Modified is not None and self.api_Expires is not None

    @classmethod
    def primary_key_row(cls):
        return cls.corporation_id