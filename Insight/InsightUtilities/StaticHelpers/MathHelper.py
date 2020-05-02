class MathHelper(object):
    @staticmethod
    def str_isk(isk_value: float, modifier_full=False):
        try:
            if isk_value >= 1e+12:
                num = float(isk_value / 1e+12)
                return "{:.1f}t".format(num) if not modifier_full else "{:.1f} trillion".format(num)
            if isk_value >= 1e+9:
                num = float(isk_value / 1e+9)
                return "{:.1f}b".format(num) if not modifier_full else "{:.1f} billion".format(num)
            elif isk_value >= 1e+6:
                num = float(isk_value / 1e+6)
                return "{:.1f}m".format(num) if not modifier_full else "{:.1f} million".format(num)
            else:
                num = float(isk_value / 1e+4)
                return "{:.1f}k".format(num) if not modifier_full else "{:.1f} thousand".format(num)
        except:
            return ""