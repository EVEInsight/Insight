from ..capRadar import *
import InsightExc


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
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.template_id = 0
            systemR = dbRow.tb_Filter_systems(30000142, self.channel_id, load_fk=False)
            systemR.max = 50000
            db.add(systemR)
            for s in self.at_ship_ids():
                db.add(dbRow.tb_Filter_types(s, self.channel_id, load_fk=False))
            db.commit()
            msg = "This Alliance Tournament ship radar feed has been converted to a full radar feed. " \
                  "The functionality of Alliance ship tracking is now integrated within the full radar service. You" \
                  " now enjoy the following features: \n\n Customizable base systems\n\n Additional optional " \
                  "tracking types/groups\n\n Mention modes"
            self.discord_client.loop.create_task(self.channel_discord_object.send(content=msg))
            raise InsightExc.DiscordError.InsightException("AT radar to capital radar conversion non-exception.")
        except Exception as ex:
            print(ex)
            raise ex
        finally:
            db.close()

    @classmethod
    def at_ship_ids(cls):
        yield 2836   # Adrestia
        yield 11936  # Apocalypse Imperial Issue
        yield 11938  # Armageddon Imperial Issue
        yield 42246  # Caedes
        yield 32788  # Cambion
        yield 33675  # Chameleon
        yield 33397  # Chremoas
        yield 32790  # Etana
        yield 35781  # Fiend
        yield 32207  # Freki
        yield 11940  # Gold Magnate
        yield 11011  # Guardian-Vexor
        yield 35779  # Imp
        yield 3516   # Malice
        yield 13202  # Megathron Federate Issue
        yield 32209  # Mimir
        yield 33395  # Moracha
        yield 635    # Opux Luxury Yacht
        yield 42245  # Rabisu
        yield 26840  # Raven State Issue
        yield 11942  # Silver Magnate
        yield 26842  # Tempest Tribal Issue
        yield 2834   # Utu
        yield 3518   # Vangel
        yield 33673  # Whiptail
        yield 45530  # Virtuoso
        yield 45531  # Victor
        yield 48636  # Hydra
        yield 48635  # Tiamat

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

    @classmethod
    def feed_category(cls):
        return 0
