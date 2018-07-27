from ..capRadar import *


class UniverseSupers(capRadar):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.max_km_age = 20
            db.merge(row)
            systemR = dbRow.tb_Filter_systems(30000142, self.channel_id)
            systemR.max = 50000
            db.merge(dbRow.tb_Filter_groups(30, self.channel_id))
            db.merge(dbRow.tb_Filter_groups(659, self.channel_id))
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return Linked_Options.opt_basicfeed(self)

    @classmethod
    def get_template_id(cls):
        return 5

    @classmethod
    def get_template_desc(cls):
        return "Universal Supers - A premade radar feed that displays recent super/titan activity regardless of standings or system."

    def __str__(self):
        return "Universal Supers Feed"
