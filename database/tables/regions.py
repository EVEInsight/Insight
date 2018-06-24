from database.tables.base_objects import *
from database.tables import *


class Regions(Base,individual_api_pulling,index_api_updating):
    __tablename__ = 'regions'

    region_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True,index=True)
    description = Column(String,default=None,nullable=True)

    api_ETag = Column(String,default=None,nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_constellations = relationship("Constellations",uselist=True, back_populates="object_region")

    def __init__(self, eve_id: int):
        self.region_id = eve_id

    def load_fk_objects(self):
        if self.__constellations:
            self.object_constellations = []
            for id in self.__constellations:
                self.object_constellations.append(database.tables.constellations.Constellations(id))

    def get_id(self):
        return self.region_id

    @classmethod
    def index_swagger_api_call(cls, api, **kwargs):
        return api.get_universe_regions_with_http_info(**kwargs)

    def get_response(self, api,**kwargs):
        return api.get_universe_regions_region_id_with_http_info(region_id=self.region_id,**kwargs)

    def process_body(self,response):
        self.name = response.get("name")
        self.description = response.get("description")
        self.__constellations= response.get("constellations")

    @classmethod
    def primary_key_row(cls):
        return cls.region_id