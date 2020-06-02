import re


class RegexCheck(object):
    eve_character_name = re.compile(r"^[a-zA-Z0-9\-\' ]+$")

    @staticmethod
    def check_regex(regex_check, query_string: str) -> bool:
        if re.fullmatch(regex_check, query_string) is None:
            return False
        else:
            return True

    @classmethod
    def is_valid_character_name(cls, character_name: str) -> bool:
        return cls.check_regex(cls.eve_character_name, character_name)
