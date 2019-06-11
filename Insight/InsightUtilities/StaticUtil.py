import InsightExc


class StaticUtil(object):
    """static utility functions"""
    @staticmethod
    def filter_type(item_list: list, filter_type: type):
        """returns a list of items of filter_type from an existing item_list"""
        return [i for i in item_list if isinstance(i, filter_type)]

    @staticmethod
    def str_to_isk(input_val: str) -> float:
        try:
            input_val = input_val.strip()
            num = "".join([c for c in input_val if c.isdigit() or c == '.'])
            n_modifier = "".join(a.casefold() for a in input_val if a.isalpha())
            num = float(num)
            if n_modifier.startswith('b'):
                num = num * 1e+9
            elif n_modifier.startswith('m'):
                num = num * 1e+6
            elif n_modifier.startswith('k'):
                num = num * 1e+3
            else:
                pass
            return num
        except:
            raise InsightExc.userInput.NotFloat
