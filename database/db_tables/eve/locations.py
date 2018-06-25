from .base_objects import *


class Locations(dec_Base.Base,name_only,):
    __tablename__ = 'locations'

    location_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True,index=True)
    pos_x = Column(Float,default=None,nullable=True)
    pos_y = Column(Float, default=None, nullable=True)
    pos_z = Column(Float, default=None, nullable=True)

    api_ETag = Column(String,default=None,nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_kills_at_location = relationship("Kills",uselist=True,back_populates="object_location")

    def __init__(self, eve_id: int):
        self.location_id = eve_id

    def get_id(self):
        return self.location_id

    def set_name(self, api_name):
        self.name = api_name

    @hybrid_property
    def need_name(self):
        return self.name == None

    @classmethod
    def primary_key_row(cls):
        return cls.location_id