class URLHelper(object):
    @staticmethod
    def type_image(type_id, resolution=512):
        try:
            if resolution <= 64:
                if resolution == 32 or resolution == 64:
                    return "https://image.eveonline.com/Type/{}_{}.png".format(type_id, resolution)
                else:
                    return "https://image.eveonline.com/Type/{}_64.png".format(type_id)
            return "https://image.eveonline.com/Render/{}_{}.png".format(type_id, resolution)
        except:
            return ""

    @staticmethod
    def zk_url(kill_id):
        try:
            return "https://zkillboard.com/kill/{}/".format(kill_id)
        except:
            return ""

    @staticmethod
    def zk_pilot(pilot_id):
        try:
            return "https://zkillboard.com/character/{}/".format(pilot_id)
        except:
            return ""

    @staticmethod
    def zk_corporation(corporation_id):
        try:
            return "https://zkillboard.com/corporation/{}/".format(corporation_id)
        except:
            return ""

    @staticmethod
    def zk_alliance(alliance_id):
        try:
            return "https://zkillboard.com/alliance/{}/".format(alliance_id)
        except:
            return ""

    @staticmethod
    def str_dotlan_map(system_name: str, region_name: str):
        try:
            s_name = system_name.replace(' ', '_')
            r_name = region_name.replace(' ', '_')
            return "http://evemaps.dotlan.net/map/{}/{}".format(r_name, s_name)
        except:
            return ""
