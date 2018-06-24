from database.tables.base_objects import *
from database.tables import *

class Attackers(Base, table_row):
    __tablename__ = 'attackers'

    no_pk = Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    kill_id = Column(Integer,ForeignKey("kills.kill_id"),nullable=False, autoincrement=False)
    character_id = Column(Integer,ForeignKey("characters.character_id"),default=None, nullable=True)
    corporation_id = Column(Integer,ForeignKey("corporations.corporation_id"), default=None, nullable=True)
    alliance_id = Column(Integer,ForeignKey("alliances.alliance_id"), default=None, nullable=True)
    damage_done = Column(Float, default=0.0, nullable=False)
    final_blow = Column(Boolean, default=False, nullable=False)
    security_status = Column(Float, default=0.0, nullable=False)
    ship_type_id = Column(Integer,ForeignKey("types.type_id"), default=None, nullable=True)
    weapon_type_id = Column(Integer,ForeignKey("types.type_id"),default=None, nullable=True)

    object_kill = relationship("Kills",uselist=False,back_populates="object_attackers")
    object_pilot = relationship("Characters",uselist=False,back_populates="object_attackers")
    object_corp = relationship("Corporations",uselist=False,back_populates="object_attackers")
    object_alliance = relationship("Alliances",uselist=False,back_populates="object_attackers")
    object_ship = relationship("Types",uselist=False,foreign_keys=[ship_type_id],back_populates="object_attacker_ships")
    object_weapon = relationship("Types",uselist=False,foreign_keys=[weapon_type_id],back_populates="object_attacker_weapons")

    def __init__(self, data: dict):
        self.character_id = data.get("character_id")
        self.corporation_id = data.get("corporation_id")
        self.alliance_id = data.get("alliance_id")
        self.damage_done = data.get("damage_done")
        self.final_blow = data.get("final_blow")
        self.security_status = data.get("security_status")
        self.ship_type_id = data.get("ship_type_id")
        self.weapon_type_id = data.get("weapon_type_id")

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
        if self.weapon_type_id:
            self.object_weapon = tb_types(self.weapon_type_id)