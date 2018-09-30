from ..capRadar import *


class OptionsRareShips(Linked_Options.opt_capradar):
    def yield_options(self):
        yield (self.InsightOptionRequired_maxage, False)
        yield (self.InsightOption_sync, False)
        yield from super(Linked_Options.opt_capradar, self).yield_options()


class RareShips(capRadar):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            systemR = dbRow.tb_Filter_systems(30000142, self.channel_id, load_fk=False)
            systemR.max = 50000
            db.add(systemR)
            ships = [2836, 11936, 11938, 42246, 32788, 33675, 33397, 32790, 35781, 32207, 11940, 11011, 35779, 3516,
                     13202, 32209, 33395, 635, 42245, 26840, 11942, 26842, 2834, 3518, 33673, 45530, 45531]
            for s in ships:
                db.add(dbRow.tb_Filter_types(s, self.channel_id, load_fk=False))
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return OptionsRareShips(self)

    @classmethod
    def get_template_id(cls):
        return 6

    @classmethod
    def get_template_desc(cls):
        return "Alliance Tournament Ship Radar - A radar feed that tracks universal AT ship activity."

    def __str__(self):
        return "Alliance Tournament Ship Activity Feed"

    @classmethod
    def is_preconfigured(cls):
        return True
