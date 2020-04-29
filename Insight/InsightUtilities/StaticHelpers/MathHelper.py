class MathHelper(object):
    @staticmethod
    def str_isk(isk_value: float):
        try:
            if isk_value >= 1000000000:
                num = float(isk_value / 1000000000)
                return '{:.1f}b'.format(num)
            elif isk_value >= 1000000:
                num = float(isk_value / 1000000)
                return '{:.1f}m'.format(num)
            else:
                num = float(isk_value / 10000)
                return '{:.1f}k'.format(num)
        except:
            return ""