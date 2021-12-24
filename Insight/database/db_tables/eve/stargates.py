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

    def session_add_nonexists_fk(self, db: Session):
        if self.system_from and not systems.Systems.session_exists(self.system_from, db):
            db.add(systems.Systems(self.system_from))
        if self.system_to and not systems.Systems.session_exists(self.system_to, db):
            db.add(systems.Systems(self.system_to))

    def compare_sde(self, other):
        return self.system_from == other.fromSolarSystemID and self.system_to == other.toSolarSystemID

    @classmethod
    def make_from_sde(cls, row):
        new_row = cls(row.fromSolarSystemID, row.toSolarSystemID)
        return new_row

    @classmethod
    def import_all_sde(cls, service_module, sde_session, sde_base):
        start = datetime.datetime.utcnow()
        db: Session = service_module.get_session()
        add_count = 0
        try:
            gates = sde_session.query(sde_base).all()
            existing_gate_pairs = set(db.query(cls.system_from, cls.system_to).all())
            for g in gates:
                if not (g.fromSolarSystemID, g.toSolarSystemID) in existing_gate_pairs:
                    new_row = cls.make_from_sde(g)
                    new_row.session_add_nonexists_fk(db)
                    db.add(new_row)
                    add_count += 1
                else:
                    pass
            db.commit()
            if add_count > 0:
                print("Imported {} {} from the SDE in {} seconds".format(str(add_count), cls.__name__, str(
                    (datetime.datetime.utcnow() - start).total_seconds())))
            else:
                print("No stargates to import")
            # for existing in db.query(cls).all():
            #     if not any(existing.compare_sde(g) for g in gates):
            #         print("Deleting gate from: {} to: {}".format(str(existing.system_from), str(existing.system_to)))
            #         db.delete(existing)
            # db.commit()
        except Exception as ex:
            print(ex)
            db.rollback()
            sde_session.rollback()
        finally:
            db.close()
            sde_session.close()


from ..eve import *
