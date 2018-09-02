class Base_Str_ATKv(object):
    def str_pilot_name(self):
        try:
            return str(self.object_pilot.character_name)
        except:
            return ""

    def str_corp_name(self):
        try:
            return str(self.object_corp.corporation_name)
        except:
            return ""

    def str_alliance_name(self):
        try:
            return str(self.object_alliance.alliance_name)
        except:
            return ""

    def str_ship_name(self):
        try:
            return str(self.object_ship.type_name)
        except:
            return ""

    def str_shipGroup_name(self):
        try:
            return str(self.object_ship.object_group.name)
        except:
            return ""

    def str_pilot_zk(self):
        try:
            return "https://zkillboard.com/character/{}/".format(str(self.character_id))
        except:
            return ""

    def str_corp_zk(self):
        try:
            return "https://zkillboard.com/corporation/{}/".format(str(self.corporation_id))
        except:
            return ""

    def str_alliance_zk(self):
        try:
            return "https://zkillboard.com/alliance/{}/".format(str(self.alliance_id))
        except:
            return ""

    def str_ship_zk(self):
        try:
            return "https://zkillboard.com/ship/{}/".format(str(self.ship_type_id))
        except:
            return ""

    def str_shipGroup_zk(self):
        try:
            return "https://zkillboard.com/group/{}/".format(str(self.object_ship.object_group.group_id))
        except:
            return ""

    def str_pilot_image(self, resolution=512):
        try:
            return "https://image.eveonline.com/Character/{}_{}.jpg".format(str(self.character_id), str(resolution))
        except:
            return ""

    def str_corp_image(self, resolution=256):
        try:
            return "https://image.eveonline.com/Corporation/{}_{}.jpg".format(str(self.corporation_id), str(resolution))
        except:
            return ""

    def str_alliance_image(self, resolution=128):
        try:
            return "https://image.eveonline.com/Alliance/{}_{}.jpg".format(str(self.alliance_id), str(resolution))
        except:
            return ""

    def str_ship_image(self, resolution=512):
        try:
            if self.object_ship.object_group.object_category.category_id == 11:
                return "https://image.eveonline.com/Type/{}_64.jpg".format(str(self.ship_type_id))
            return "https://image.eveonline.com/Render/{}_{}.jpg".format(str(self.ship_type_id), str(resolution))
        except:
            return ""

    def str_highest_name(self):
        return_str = ""
        try:
            return_str = self.str_corp_name() if self.corporation_id is not None else return_str
            return_str = self.str_alliance_name() if self.alliance_id is not None else return_str
        except:
            pass
        finally:
            return str(return_str)

    def str_highest_zk(self):
        return_str = ""
        try:
            return_str = self.str_corp_zk() if self.corporation_id is not None else return_str
            return_str = self.str_alliance_zk() if self.alliance_id is not None else return_str
        except:
            pass
        finally:
            return return_str

    def str_highest_image(self, resolution=128):
        return_str = ""
        try:
            return_str = self.str_corp_image(resolution) if self.corporation_id is not None else return_str
            return_str = self.str_alliance_image() if self.alliance_id is not None else return_str
        except:
            pass
        finally:
            return return_str
