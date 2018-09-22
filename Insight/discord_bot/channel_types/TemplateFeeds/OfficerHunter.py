from ..capRadar import *


class OfficerHunter(capRadar):
    def template_loader(self):
        self.general_table().reset_filters(self.channel_id, self.service)
        db: Session = self.service.get_session()
        try:
            row = db.query(self.linked_table()).filter(self.linked_table().channel_id == self.channel_id).one()
            row.max_km_age = 120
            db.merge(row)
            systemR = dbRow.tb_Filter_systems(30000142, self.channel_id)
            systemR.max = 50000
            db.merge(systemR)
            db.merge(dbRow.tb_Filter_groups(553, self.channel_id))  # angels
            db.merge(dbRow.tb_Filter_groups(559, self.channel_id))  # br
            db.merge(dbRow.tb_Filter_groups(564, self.channel_id))  # guristas
            db.merge(dbRow.tb_Filter_groups(569, self.channel_id))  # sansha
            db.merge(dbRow.tb_Filter_groups(574, self.channel_id))  # serpentis
            db.merge(dbRow.tb_Filter_groups(1174, self.channel_id))  # drones
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    def get_linked_options(self):
        return Linked_Options.opt_basicfeed(self)

    async def command_sync(self, message_object):
        await super(capRadar, self).command_sync(message_object)

    async def background_contact_sync(self, message=None, suppress=False):  # override, no contacts to sync
        pass

    @classmethod
    def get_template_id(cls):
        return 4

    @classmethod
    def get_template_desc(cls):
        return "Officer Hunter - A radar feed that displays officer activity when an npc officer is on a killmail."

    def __str__(self):
        return "Officer Hunter Feed"

    def make_derived_visual(self, visual_class):
        class VisualOfficerHunter(visual_class):
            def set_frame_color(self):
                self.embed.color = discord.Color(12303149)

        return VisualOfficerHunter

    @classmethod
    def is_preconfigured(cls):
        return True
