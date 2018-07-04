from .base_objects import *


class Characters(dec_Base.Base,name_only):
    __tablename__ = 'characters'

    character_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    character_name = Column(String,default=None,nullable=True,index=True)

    api_ETag = Column(String,default=None,nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_attackers = relationship("Attackers", uselist=True,back_populates="object_pilot")
    object_loses = relationship("Victims", uselist=True, back_populates="object_pilot")
    object_filters = relationship("Filter_characters", uselist=True, back_populates="object_item")

    def __init__(self, pilot_id: int):
        self.character_id = pilot_id

    def get_id(self):
        return self.character_id

    def set_name(self, api_name):
        self.character_name = api_name

    def get_name(self):
        return self.character_name

    @hybrid_property
    def need_name(self):
        return self.character_name == None

    @classmethod
    def primary_key_row(cls):
        return cls.character_id
