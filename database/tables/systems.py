from database.tables.base_objects import *
from database.tables import *


class Systems(Base,name_only,individual_api_pulling,index_api_updating):
    __tablename__ = 'systems'

    system_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True,index=True)
    constellation_id = Column(Integer, ForeignKey("constellations.constellation_id"),nullable=True)
    security_class = Column(String,default=None, nullable=True)
    security_status = Column(Float,default=0.0, nullable=True)
    star_id = Column(Integer,default=None,nullable=True)

    pos_x = Column(Float,default=None,nullable=True)
    pos_y = Column(Float, default=None, nullable=True)
    pos_z = Column(Float, default=None, nullable=True)

    api_ETag = Column(String,default=None,nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_constellation = relationship("Constellations", uselist=False, back_populates="object_systems",lazy="joined")
    object_kills_in_system = relationship("Kills",uselist=True,back_populates="object_system")

    def __init__(self, eve_id: int):
        self.system_id = eve_id

    def load_fk_objects(self):
        if self.constellation_id:
            self.object_constellation = database.tables.constellations.Constellations(self.constellation_id)

    def get_id(self):
        return self.system_id

    def set_name(self, api_name):
        self.name = api_name

    @classmethod
    def index_swagger_api_call(cls, api, **kwargs):
        return api.get_universe_systems_with_http_info(**kwargs)

    def get_response(self, api,**kwargs):
        return api.get_universe_systems_system_id_with_http_info(system_id=self.system_id,**kwargs)

    def process_body(self,response):
        self.name = response.get("name")
        self.constellation_id = response.get("constellation_id")
        self.security_class = response.get("security_class")
        self.security_status = response.get("security_status")
        self.star_id = response.get("star_id")
        self.pos_x = response.get("position").get("x")
        self.pos_y = response.get("position").get("y")
        self.pos_z = response.get("position").get("z")

    @hybrid_property
    def need_name(self):
        return self.name == None

    @classmethod
    def primary_key_row(cls):
        return cls.system_id
