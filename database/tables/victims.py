from database.tables.base_objects import *
from database.tables import *


class Victims(Base, table_row):
    __tablename__ = 'Victims'

    kill_id = Column(Integer,ForeignKey("kills.kill_id"), primary_key=True,nullable=False, autoincrement=False)
    character_id = Column(Integer,ForeignKey("characters.character_id"),default=None, nullable=True)
    corporation_id = Column(Integer,ForeignKey("corporations.corporation_id"), default=None, nullable=True)
    alliance_id = Column(Integer,ForeignKey("alliances.alliance_id"), default=None, nullable=True)
    damage_taken = Column(Float, default=0.0, nullable=False)
    pos_x = Column(Float, default=0, nullable=False)
    pos_y = Column(Float,default=0,nullable=False)
    pos_z = Column(Float,default=0,nullable=False)
    ship_type_id = Column(Integer,ForeignKey("types.type_id"), default=None, nullable=True)

    object_kill = relationship("Kills",uselist=False,back_populates="object_victim")
    object_pilot = relationship("Characters",uselist=False,back_populates="object_loses")
    object_corp = relationship("Corporations",uselist=False,back_populates="object_loses")
    object_alliance = relationship("Alliances",uselist=False,back_populates="object_loses")
    object_ship = relationship("Types",uselist=False,back_populates="object_loses_ships")

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
            self.object_pilot = tb_characters(self.character_id)
        if self.corporation_id:
            self.object_corp = tb_corporations(self.corporation_id)
        if self.alliance_id:
            self.object_alliance = tb_alliances(self.alliance_id)
        if self.ship_type_id:
            self.object_ship = tb_types(self.ship_type_id)