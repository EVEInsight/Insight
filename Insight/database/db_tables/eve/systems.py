from .base_objects import *
from . import constellations
from .sde_importer import *
import math


class Systems(dec_Base.Base,name_only,individual_api_pulling,index_api_updating,sde_impoter):
    __tablename__ = 'systems'

    system_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True, index=True)
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
            self.object_constellation = constellations.Constellations(self.constellation_id)

    def get_id(self):
        return self.system_id

    def set_name(self, api_name):
        self.name = api_name

    def __str__(self):
        try:
            return "{}({})".format(str(self.name), str(self.object_constellation.object_region.name))
        except:
            return "{}".format(str(self.name))

    def ly_range(self, other):
        other_x = 0
        other_y = 0
        other_z = 0
        if isinstance(other, Systems):
            other_x, other_y, other_z = other.pos_x, other.pos_y, other.pos_z
        if isinstance(other, tb_Filter_systems):
            other_x, other_y, other_z = other.object_item.pos_x, other.object_item.pos_y, other.object_item.pos_z
        return math.sqrt(
            pow(self.pos_x - other_x, 2) + pow(self.pos_y - other_y, 2) + pow(self.pos_z - other_z, 2)) / 9.4605284e15

    def compare_range(self, other):
        if isinstance(other, tb_Filter_systems):
            return other.max >= self.ly_range(other)
        return False

    def compare_filter(self, other):
        if isinstance(other, Systems):
            return self.system_id == other.system_id
        if isinstance(other, tb_Filter_systems):
            return self.system_id == other.filter_id
        if isinstance(other, tb_Filter_constellations):
            try:
                return self.object_constellation.constellation_id == other.filter_id
            except Exception as ex:
                print(ex)
                return False
        if isinstance(other, tb_Filter_regions):
            try:
                return self.object_constellation.object_region.region_id == other.filter_id
            except Exception as ex:
                print(ex)
                return False
        return False

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

    @classmethod
    def make_from_sde(cls,__row):
        new_row = cls(__row.solarSystemID)
        new_row.name = __row.solarSystemName
        new_row.constellation_id = __row.constellationID
        new_row.security_class = __row.securityClass
        new_row.security_status = __row.security
        #new_row.star_id = __row.sunTypeID location?
        new_row.pos_x = __row.x
        new_row.pos_y = __row.y
        new_row.pos_z = __row.z
        new_row.load_fk_objects()
        return new_row

    @hybrid_property
    def need_api(self):
        return self.name is None or self.constellation_id is None or self.pos_x is None or self.pos_y is None or self.pos_y is None

    @need_api.expression
    def need_api(cls):
        return or_(cls.name.is_(None),cls.constellation_id.is_(None),cls.pos_x.is_(None),cls.pos_y.is_(None),cls.pos_z.is_(None))

    @classmethod
    def get_missing_ids(cls,service_module,sde_session,sde_base):
        existing_ids = [i.system_id for i in service_module.get_session().query(cls.system_id).filter(not_(cls.need_api)).all()]
        importing_ids = [i.solarSystemID for i in sde_session.query(sde_base.solarSystemID).all()]
        return list(set(importing_ids)-set(existing_ids))

    @classmethod
    def get_query_filter(cls,sde_base):
        return sde_base.solarSystemID

    def str_system_name(self, url_safe=False):
        try:
            return str(self.name) if not url_safe else str(self.name).replace(' ', '_')
        except:
            return ""

    def str_region_name(self, url_safe=False):
        try:
            reg = self.object_constellation.object_region
            return str(reg.name) if not url_safe else str(reg.name).replace(' ', '_')
        except:
            return ""

    def str_dotlan(self):
        try:
            return "http://evemaps.dotlan.net/system/{}".format(self.str_system_name(True))
        except:
            return ""

    def str_dotlan_map(self):
        try:
            return "http://evemaps.dotlan.net/map/{}/{}".format(self.str_region_name(True), self.str_system_name(True))
        except:
            return ""

    def str_dotlan_jmp(self, to_sys, ship_group=""):
        try:
            assert isinstance(to_sys, Systems)
            return "http://evemaps.dotlan.net/jump/{sg},555/{b}:{t}".format(sg=ship_group, b=self.str_system_name(True),
                                                                            t=to_sys.str_system_name(True))
        except:
            return ""

    def str_dotlan_gates(self, to_sys):
        try:
            assert isinstance(to_sys, Systems)
            return "http://evemaps.dotlan.net/route/{b}:{t}".format(b=self.str_system_name(True),
                                                                    t=to_sys.str_system_name(True))
        except:
            return ""

    def str_jmp_titan(self, to_sys):
        return self.str_dotlan_jmp(to_sys, "Avatar")

    def str_jmp_carrier(self, to_sys):
        return self.str_dotlan_jmp(to_sys, "Archon")

    def str_jmp_blops(self, to_sys):
        return self.str_dotlan_jmp(to_sys, "Redeemer")


from ..filters import *
from ..eve import *
