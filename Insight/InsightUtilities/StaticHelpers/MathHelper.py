class MathHelper(object):
    @staticmethod
    def str_isk(isk_value: float, modifier_full=False):
        try:
            if isk_value >= 1e+12:
                num = float(isk_value / 1e+12)
                return "{:.1f}t".format(num) if not modifier_full else "{:.1f} trillion".format(num)
            elif isk_value >= 1e+9:
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

    @staticmethod
    def str_min_seconds_convert(seconds_input: float, modifier_full=False):
        try:
            if seconds_input >= 3.154e+7:
                num = float(seconds_input / 3.154e+7)
                return "{:.1f}y".format(num) if not modifier_full else "{:.1f} year".format(num)
            elif seconds_input >= 86400:
                num = float(seconds_input / 86400)
                return "{:.0f}d".format(num) if not modifier_full else "{:.1f} day".format(num)
            elif seconds_input >= 3600:
                num = float(seconds_input / 3600)
                return "{:.0f}h".format(num) if not modifier_full else "{:.1f} hour".format(num)
            elif seconds_input >= 60:
                num = float(seconds_input / 60)
                return "{:.0f}m".format(num) if not modifier_full else "{:.1f} minute".format(num)
            else:
                return "{:.0f}s".format(seconds_input) if not modifier_full else "{:.1f} second".format(seconds_input)
        except:
            return ""

    @staticmethod
    def percent_convert(normalized_percent: float, decimal_positions: int = 0):
        return "{:.{}f}%".format(normalized_percent * 100, decimal_positions)
