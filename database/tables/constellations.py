from database.tables.base_objects import *
from database.tables import *


class Constellations(Base,individual_api_pulling,index_api_updating):
    __tablename__ = 'constellations'

    constellation_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True,index=True)
    pos_x = Column(Float,default=None,nullable=True)
    pos_y = Column(Float, default=None, nullable=True)
    pos_z = Column(Float, default=None, nullable=True)
    region_id = Column(Integer, ForeignKey("regions.region_id"),nullable=True)

    api_ETag = Column(String,default=None,nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_region = relationship("Regions", uselist=False, back_populates="object_constellations")
    object_systems = relationship("Systems",uselist=True, back_populates="object_constellation")

    def __init__(self, eve_id: int):
        self.constellation_id = eve_id

    def load_fk_objects(self):
        if self.region_id:
            self.object_region = tb_regions(self.region_id)
        if self.__systems:
            self.object_systems = []
            for system_id in self.__systems:
                self.object_systems.append(database.tables.systems.Systems(system_id))

    def get_id(self):
        return self.constellation_id

    @classmethod
    def index_swagger_api_call(cls, api, **kwargs):
        return api.get_universe_constellations_with_http_info(**kwargs)

    def get_response(self, api,**kwargs):
        return api.get_universe_constellations_constellation_id_with_http_info(constellation_id=self.constellation_id,**kwargs)

    def process_body(self,response):
        self.name = response.get("name")
        self.region_id = response.get("region_id")
        self.pos_x = response.get("position").get("x")
        self.pos_y = response.get("position").get("y")
        self.pos_z = response.get("position").get("z")
        self.__systems = response.get("systems")

    @classmethod
    def primary_key_row(cls):
        return cls.constellation_id