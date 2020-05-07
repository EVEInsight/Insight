from .base_objects import *
from . import characters,corporations,alliances,types
from .Base_Str_ATKv import Base_Str_ATKv


class Victims(dec_Base.Base, table_row, Base_Str_ATKv):
    __tablename__ = 'victims'

    kill_id = Column(Integer,ForeignKey("kills.kill_id"), primary_key=True,nullable=False, autoincrement=False)
    character_id = Column(Integer,ForeignKey("characters.character_id"),default=None, nullable=True, index=True)
    corporation_id = Column(Integer,ForeignKey("corporations.corporation_id"), default=None, nullable=True, index=True)
    alliance_id = Column(Integer,ForeignKey("alliances.alliance_id"), default=None, nullable=True, index=True)
    damage_taken = Column(Float, default=0.0, nullable=False)
    pos_x = Column(Float, default=0, nullable=False)
    pos_y = Column(Float,default=0,nullable=False)
    pos_z = Column(Float,default=0,nullable=False)
    ship_type_id = Column(Integer,ForeignKey("types.type_id"), default=None, nullable=True)

    object_kill = relationship("Kills",uselist=False,back_populates="object_victim")
    object_pilot = relationship("Characters",uselist=False,back_populates="object_loses",lazy="joined")
    object_corp = relationship("Corporations",uselist=False,back_populates="object_loses",lazy="joined")
    object_alliance = relationship("Alliances",uselist=False,back_populates="object_loses",lazy="joined")
    object_ship = relationship("Types",uselist=False,back_populates="object_loses_ships",lazy="joined")

    def __init__(self, data: dict):
        self.character_id = data.get("character_id")
        self.corporation_id = data.get("corporation_id")
        self.alliance_id = data.get("alliance_id")
        self.damage_taken = data.get("damage_taken")
        self.ship_type_id = data.get("ship_type_id")
        self.__pos_dict = data.get("position")
        if self.__pos_dict:
            self.pos_x = self.__pos_dict.get("x")
            self.pos_y = self.__pos_dict.get("y")
            self.pos_z = self.__pos_dict.get("z")
        self.load_objects()

    def load_objects(self):
        if self.character_id:
            self.object_pilot = characters.Characters(self.character_id)
        if self.corporation_id:
            self.object_corp = corporations.Corporations(self.corporation_id)
        if self.alliance_id:
            self.object_alliance = alliances.Alliances(self.alliance_id)
        if self.ship_type_id:
            self.object_ship = types.Types(self.ship_type_id)

    def compare_filter_list(self, other):
        if isinstance(other,tb_Filter_characters):
            return self.character_id == other.filter_id
        if isinstance(other,tb_Filter_corporations):
            return self.corporation_id == other.filter_id
        if isinstance(other,tb_Filter_alliances):
            return self.alliance_id == other.filter_id
        if isinstance(other,tb_Filter_types):
            return self.ship_type_id == other.filter_id
        if isinstance(other,tb_Filter_groups):
            try:
                compare: tb_types = self.object_ship
                return compare.group_id == other.filter_id
            except Exception as ex:
                print(ex)
                return False
        if isinstance(other,tb_Filter_categories):
            try:
                compare: tb_groups = self.object_ship.object_group
                return compare.category_id == other.filter_id
            except Exception as ex:
                print(ex)
                return False
        return False

    def to_jsonDictionary(self) -> dict:
        return {
            "alliance_id": self.alliance_id,
            "character_id": self.character_id,
            "corporation_id": self.corporation_id,
            "damage_taken": self.damage_taken,
            "items": [],
            "position": {
                "x": self.pos_x,
                "y": self.pos_y,
                "z": self.pos_z
            },
            "ship_type_id": self.ship_type_id,
            "character": self.object_pilot.to_jsonDictionary() if self.object_pilot else None,
            "corporation": self.object_corp.to_jsonDictionary() if self.object_corp else None,
            "alliance": self.object_alliance.to_jsonDictionary() if self.object_alliance else None,
            "ship": self.object_ship.to_jsonDictionary() if self.object_ship else None
        }


from ..filters import *
from ..eve import *