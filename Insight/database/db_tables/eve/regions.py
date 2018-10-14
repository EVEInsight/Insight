from .base_objects import *
from . import constellations
from .sde_importer import *
from sqlalchemy import case


class Regions(dec_Base.Base,individual_api_pulling,index_api_updating,sde_impoter):
    __tablename__ = 'regions'

    region_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True, index=True)
    description = Column(String,default=None,nullable=True)

    api_ETag = Column(String,default=None,nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_constellations = relationship("Constellations",uselist=True, back_populates="object_region")

    def __init__(self, eve_id: int):
        self.region_id = eve_id
        self.__constellations = None

    def load_fk_objects(self):
        if self.__constellations:
            self.object_constellations = []
            for id in self.__constellations:
                self.object_constellations.append(constellations.Constellations(id))

    def get_id(self):
        return self.region_id

    def __str__(self):
        return "{}".format(str(self.name))

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

    @classmethod
    def make_from_sde(cls,__row):
        new_row = cls(__row.regionID)
        new_row.name = __row.regionName
        new_row.load_fk_objects()
        return new_row

    @hybrid_property
    def need_api(self):
        return self.name is None

    @need_api.expression
    def need_api(cls):
        return cls.name.is_(None)

    @classmethod
    def get_missing_ids(cls, service_module, sde_session, sde_base):
        existing_ids = [i.region_id for i in
                        service_module.get_session().query(cls.region_id).filter(not_(cls.need_api)).all()]
        importing_ids = [i.regionID for i in sde_session.query(sde_base.regionID).all()]
        return list(set(importing_ids) - set(existing_ids))

    @classmethod
    def get_query_filter(cls, sde_base):
        return sde_base.regionID