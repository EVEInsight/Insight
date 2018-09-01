from .base_objects import *
from .sde_importer import *
from . import groups


class Types(dec_Base.Base,name_only,index_api_updating,sde_impoter):
    __tablename__ = 'types'

    type_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    type_name = Column(String,default=None,nullable=True)
    description = Column(String,default="")
    basePrice = Column(DECIMAL(19,4),default=None,nullable=True)
    group_id = Column(Integer,ForeignKey("groups.group_id"),nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_group = relationship("Groups",uselist=False,back_populates="object_types",lazy="joined")
    object_attacker_ships = relationship("Attackers", uselist=True,foreign_keys="Attackers.ship_type_id",back_populates="object_ship")
    object_attacker_weapons = relationship("Attackers", uselist=True,foreign_keys="Attackers.weapon_type_id",back_populates="object_weapon")
    object_loses_ships = relationship("Victims", uselist=True, back_populates="object_ship")

    def __init__(self, type_id: int):
        self.type_id = type_id

    def load_fk_objects(self):
        if self.group_id:
            self.object_group = groups.Groups(self.group_id)

    def get_id(self):
        return self.type_id

    def get_name(self):
        return self.type_name

    def set_name(self, api_name):
        self.type_name = api_name

    @classmethod
    def index_swagger_api_call(cls, api, **kwargs):
        return api.get_universe_types_with_http_info(**kwargs)

    @hybrid_property
    def need_name(self):
        return self.type_name == None

    @classmethod
    def primary_key_row(cls):
        return cls.type_id

    @classmethod
    def make_from_sde(cls,__row):
        new_row = cls(__row.typeID)
        new_row.type_name = __row.typeName
        new_row.group_id = __row.groupID
        new_row.description = __row.description
        new_row.basePrice = __row.basePrice
        new_row.load_fk_objects()
        return new_row

    @hybrid_property
    def need_api(self):
        return self.type_name is None or self.group_id is None

    @need_api.expression
    def need_api(cls):
        return or_(cls.type_name.is_(None), cls.group_id.is_(None))

    @classmethod
    def get_missing_ids(cls, service_module, sde_session, sde_base):
        existing_ids = [i.type_id for i in
                        service_module.get_session().query(cls.type_id).filter(not_(cls.need_api)).all()]
        importing_ids = [i.typeID for i in sde_session.query(sde_base.typeID).all()]
        return list(set(importing_ids) - set(existing_ids))

    @classmethod
    def get_query_filter(cls, sde_base):
        return sde_base.typeID

