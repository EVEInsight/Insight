from .base_objects import *
from . import regions,systems
from .sde_importer import *


class Constellations(dec_Base.Base, name_only, individual_api_pulling, index_api_updating, sde_impoter):
    __tablename__ = 'constellations'

    constellation_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True, index=True)
    pos_x = Column(Float,default=None,nullable=True)
    pos_y = Column(Float, default=None, nullable=True)
    pos_z = Column(Float, default=None, nullable=True)
    region_id = Column(Integer, ForeignKey("regions.region_id"),nullable=True)

    api_ETag = Column(String,default=None,nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_region = relationship("Regions", uselist=False, back_populates="object_constellations", lazy="joined")
    object_systems = relationship("Systems",uselist=True, back_populates="object_constellation")

    def __init__(self, eve_id: int):
        self.constellation_id = eve_id
        self.__systems = None

    def load_fk_objects(self):
        if self.region_id:
            self.object_region = regions.Regions(self.region_id)
        if self.__systems:
            self.object_systems = []
            for system_id in self.__systems:
                self.object_systems.append(systems.Systems(system_id))

    def get_id(self):
        return self.constellation_id

    def set_name(self, api_name):
        self.name = api_name

    def get_name(self):
        return self.name

    @hybrid_property
    def need_name(self):
        return self.name == None

    def __str__(self):
        try:
            return "{}({})".format(str(self.name), str(self.object_region.name))
        except:
            return "{}".format(str(self.name))

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

    @classmethod
    def make_from_sde(cls,__row):
        new_row = cls(__row.constellationID)
        new_row.name = __row.constellationName
        new_row.region_id = __row.regionID
        new_row.pos_x = __row.x
        new_row.pos_y = __row.y
        new_row.pos_z = __row.z
        new_row.load_fk_objects()
        return new_row

    @hybrid_property
    def need_api(self):
        return self.name is None or self.region_id is None

    @need_api.expression
    def need_api(cls):
        return or_(cls.name.is_(None),cls.region_id.is_(None))

    @classmethod
    def get_missing_ids(cls, service_module, sde_session, sde_base):
        existing_ids = [i.constellation_id for i in
                        service_module.get_session().query(cls.constellation_id).filter(not_(cls.need_api)).all()]
        importing_ids = [i.constellationID for i in sde_session.query(sde_base.constellationID).all()]
        return list(set(importing_ids) - set(existing_ids))

    @classmethod
    def get_query_filter(cls, sde_base):
        return sde_base.constellationID
