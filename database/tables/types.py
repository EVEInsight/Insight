from database.tables.base_objects import *


class Types(Base,name_only,index_api_updating):
    __tablename__ = 'types'

    type_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    type_name = Column(String,default=None,nullable=True,index=True)
    group_id = Column(Integer,ForeignKey("groups.group_id"),nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_group = relationship("Groups",uselist=False,back_populates="object_types")
    object_attacker_ships = relationship("Attackers", uselist=True,foreign_keys="Attackers.ship_type_id",back_populates="object_ship")
    object_attacker_weapons = relationship("Attackers", uselist=True,foreign_keys="Attackers.weapon_type_id",back_populates="object_weapon")
    object_loses_ships = relationship("Victims", uselist=True, back_populates="object_ship")

    def __init__(self, type_id: int):
        self.type_id = type_id

    def get_id(self):
        return self.type_id

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

