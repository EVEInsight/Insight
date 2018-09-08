from .base_objects import *
from .sde_importer import *


class Stargates(dec_Base.Base, sde_impoter, individual_api_pulling):
    __tablename__ = 'stargates'

    system_from = Column(Integer, ForeignKey("systems.system_id"), primary_key=True, nullable=False, autoincrement=False)
    system_to = Column(Integer, ForeignKey("systems.system_id"), primary_key=True, nullable=False, autoincrement=False)

    object_system_from = relationship("Systems", uselist=False, foreign_keys=[system_from])
    object_system_to = relationship("Systems", uselist=False, foreign_keys=[system_to])

    def __init__(self, system_from: int, system_to):
        self.system_from = system_from
        self.system_to = system_to

    def load_fk_objects(self):
        self.object_system_from = systems.Systems(self.system_from)
        self.object_system_to = systems.Systems(self.system_to)

    def compare_sde(self, other):
        return self.system_from == other.fromSolarSystemID and self.system_to == other.toSolarSystemID

    @classmethod
    def make_from_sde(cls, row):
        new_row = cls(row.fromSolarSystemID, row.toSolarSystemID)
        new_row.load_fk_objects()
        return new_row

    @classmethod
    def import_all_sde(cls, service_module, sde_session, sde_base):
        start = datetime.datetime.utcnow()
        db: Session = service_module.get_session()
        add_count = 0
        try:
            gates = sde_session.query(sde_base).all()
            for g in gates:
                r = db.query(cls).filter(cls.system_from == g.fromSolarSystemID, cls.system_to == g.toSolarSystemID).one_or_none()
                if r is None:
                    db.merge(cls.make_from_sde(g))
                    add_count += 1
            db.commit()
            if add_count > 0:
                print("Imported {} {} from the SDE in {} seconds".format(str(add_count), cls.__name__, str(
                    (datetime.datetime.utcnow() - start).total_seconds())))
            else:
                print("No stargates to import.")
            # for existing in db.query(cls).all():
            #     if not any(existing.compare_sde(g) for g in gates):
            #         print("Deleting gate from: {} to: {}".format(str(existing.system_from), str(existing.system_to)))
            #         db.delete(existing)
            # db.commit()
        except Exception as ex:
            print(ex)


from ..eve import *
