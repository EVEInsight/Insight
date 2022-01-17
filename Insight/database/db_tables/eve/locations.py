from .base_objects import *
from .sde_importer import sde_impoter
from InsightUtilities.StaticHelpers import URLHelper


class Locations(dec_Base.Base,table_row,sde_impoter):
    __tablename__ = 'locations'

    location_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True)
    typeID = Column(Integer,ForeignKey("types.type_id"),nullable=True, index=True)
    groupID = Column(Integer,ForeignKey("groups.group_id"),nullable=True, index=True)
    pos_x = Column(Float,default=None,nullable=True)
    pos_y = Column(Float, default=None, nullable=True)
    pos_z = Column(Float, default=None, nullable=True)
    radius = Column(Float,default=None,nullable=True)

    object_kills_at_location = relationship("Kills",uselist=True,back_populates="object_location")
    object_type = relationship("Types",uselist=False,lazy="joined")
    object_group = relationship("Groups",uselist=False,lazy="joined")

    def __init__(self, eve_id: int):
        self.location_id = eve_id

    def session_add_nonexists_fk(self, db: Session):
        if self.typeID and not types.Types.session_exists(self.typeID, db):
            db.add(types.Types(self.typeID))
        if self.groupID and not groups.Groups.session_exists(self.groupID, db):
            db.add(groups.Groups(self.groupID))

    def get_id(self):
        return self.location_id

    @classmethod
    def primary_key_row(cls):
        return cls.location_id

    @hybrid_property
    def need_api(self):
        return self.name is None

    @need_api.expression
    def need_api(cls):
        return cls.name.is_(None)

    @classmethod
    def make_from_sde(cls,__row):
        new_row = cls(__row.itemID)
        new_row.name = __row.itemName
        new_row.typeID = __row.typeID
        new_row.groupID = __row.groupID if __row.groupID >= 0 else None  #todo location 40009087 in mapDemoralize has an invalid group id of -1. Might be error in either sde or esi. Location is Jita IV - Moon 4
        new_row.pos_x = __row.x
        new_row.pos_y = __row.y
        new_row.pos_z = __row.z
        new_row.radius = __row.radius
        return new_row

    @classmethod
    def get_missing_ids(cls, service_module, sde_session, sde_base):
        existing_ids = [i.location_id for i in
                        service_module.get_session().query(cls.location_id).filter(not_(cls.need_api)).all()]
        importing_ids = [i.itemID for i in sde_session.query(sde_base.itemID).all()]
        return list(set(importing_ids) - set(existing_ids))

    @classmethod
    def import_stargates(cls, service_module, sde_session, sde_base):
        db: Session = service_module.get_session()
        try:
            missing_items = db.query(cls).filter(cls.name == None).all()
            length_missing_ids = len(missing_items)
            if length_missing_ids > 0:
                print("Need to import stargate names for {} {}".format(str(length_missing_ids), cls.__name__))
            else:
                return
            for chunk in name_only.split_lists(missing_items, 75000):
                start = datetime.datetime.utcnow()
                try:
                    for item in chunk:
                        try:
                            __row = sde_session.query(sde_base).filter(sde_base.itemID == item.location_id).one_or_none()
                            if __row is None: # does not exist in SDE
                                item.name = "!!UNKNOWN LOCATION!!"
                            else:
                                item.name = __row.itemName
                            db.merge(item)
                        except Exception as ex:
                            print(ex)
                    db.commit()
                    print("Imported {} {} from the SDE in {} seconds".format(str(len(chunk)), cls.__name__, str(
                        (datetime.datetime.utcnow() - start).total_seconds())))
                except Exception as ex:
                    print(ex)
                    db.rollback()
        except Exception as ex:
            print(ex)
            db.rollback()
            sde_session.rollback()
        finally:
            db.close()
            sde_session.close()

    @classmethod
    def get_query_filter(cls, sde_base):
        return sde_base.itemID

    def to_jsonDictionary(self) -> dict:
        return {
            "location_id": self.location_id,
            "location_name": self.name,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "pos_z": self.pos_z,
            "radius": self.radius,
            "type": self.object_type.to_jsonDictionary() if self.object_type else None,
            "group": self.object_group.to_jsonDictionary() if self.object_group else None,
            "urlZK": URLHelper.zk_location(self.location_id)
        }


from . import types,groups