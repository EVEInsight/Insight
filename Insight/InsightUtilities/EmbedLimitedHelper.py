import discord
from discord.embeds import EmptyEmbed
from InsightExc import Utilities
from datetime import datetime


class EmbedLimitedHelper(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.limit_total_fields = 25
        self.limit_total_char = 5500
        self.limit_author_name = 256
        self.limit_field_name = 256
        self.limit_field_value = 1024
        self.limit_description = 2048
        self.limit_footer_text = 2048
        self.limit_title = 256
        self.count_fields = 0
        self.count_total_chars = 0

        self.field_start_chars = ""
        self.field_end_chars = ""
        self.field_buffer_length = 0
        self.field_bound_length = 0
        self.field_buffer = ""
        self.field_buffer_current = ""
        self.field_buffer_name = ""
        self.field_buffer_continued_name = ""
        self.field_buffer_is_continued = False
        self.field_buffer_inline = False

    def _increment_counter(self, increment_length):
        if (self.count_total_chars + increment_length >= self.limit_total_char) or \
                ((len(self) + increment_length) >= self.limit_total_char):
            raise Utilities.EmbedMaxTotalCharLimit
        else:
            self.count_total_chars += increment_length

    def _char_check(self, current_length: int, limit_length: int):
        if current_length >= limit_length:
            raise Utilities.EmbedItemCharLimit(current_length, limit_length)

    def char_count(self, *args):
        operation_total = 0
        for s in args:
            operation_total += len(s)
        return operation_total

    def set_image(self, *, url):
        self._increment_counter(self.char_count(url))
        super().set_image(url=url)

    def set_thumbnail(self, *, url):
        self._increment_counter(self.char_count(url))
        super().set_thumbnail(url=url)

    def set_color(self, color: discord.Color):
        self.color = color

    def set_author(self, *, name, url=EmptyEmbed, icon_url=EmptyEmbed):
        char_count = 0
        if isinstance(url, str):
            char_count += self.char_count(url)
        if isinstance(icon_url, str):
            char_count += self.char_count(icon_url)

        name_length = self.char_count(icon_url)
        self._char_check(name_length, self.limit_author_name)
        char_count += name_length

        self._increment_counter(char_count)
        super().set_author(name=name, url=url, icon_url=icon_url)

    def field_buffer_start_bounds(self, start_chars: str = "", end_chars: str = ""):
        self.field_start_chars = start_chars
        self.field_end_chars = end_chars
        self.field_bound_length = len(self.field_start_chars) + len(self.field_end_chars)

    def field_buffer_end_bounds(self):
        self._field_buffer_encase()
        self.field_start_chars = ""
        self.field_end_chars = ""

    def field_buffer_start(self, name: str, name_continued: str, inline=False):
        if self.field_buffer_current or self.field_buffer:
            self.field_buffer_end()
        self.field_start_chars = ""
        self.field_end_chars = ""
        self.field_buffer_is_continued = False
        self.field_buffer_inline = inline
        self.field_buffer_name = name
        self.field_buffer_continued_name = name_continued

    def field_buffer_end(self):
        self._field_buffer_finalize()
        self.field_buffer_is_continued = False
        self.field_buffer_name = ""
        self.field_buffer_continued_name = ""

    def field_buffer_add(self, value: str, no_new_line=False):
        if not no_new_line:
            value_insert = "{}\n".format(value)
        else:
            value_insert = value
        length_new_line = len(value_insert)
        if self.field_buffer_length + length_new_line + self.field_bound_length >= self.limit_field_value:
            self._field_buffer_finalize()
        self.field_buffer_length += length_new_line
        self.field_buffer_current += value_insert

    def _field_buffer_encase(self):
        self.field_buffer += "{}{}{}".format(self.field_start_chars, self.field_buffer_current, self.field_end_chars)
        self.field_buffer_current = ""

    def _field_buffer_finalize(self):
        self._field_buffer_encase()
        field_name = self.field_buffer_name if not self.field_buffer_is_continued else self.field_buffer_continued_name
        self.add_field(name=field_name, value=self.field_buffer, inline=self.field_buffer_inline)
        self.field_buffer = ""
        self.field_buffer_current = ""
        self.field_buffer_is_continued = True
        self.field_buffer_length = 0

    def add_field(self, *, name, value, inline=True):
        char_count = 0

        name_length = self.char_count(name)
        self._char_check(name_length, self.limit_field_name)
        char_count += name_length

        value_length = self.char_count(value)
        self._char_check(value_length, self.limit_field_value)
        char_count += value_length

        if (self.count_fields + 1) > self.limit_total_fields:
            raise Utilities.EmbedMaxTotalFieldsLimit
        self._increment_counter(char_count)
        self.count_fields += 1
        super().add_field(name=name, value=value, inline=inline)

    def set_description(self, description: str):
        char_count = self.char_count(description)
        self._char_check(char_count, self.limit_description)
        self._increment_counter(char_count)
        self.description = description

    def set_footer(self, *, text=EmptyEmbed, icon_url=EmptyEmbed):
        char_count = 0
        if isinstance(text, str):
            text_length = self.char_count(text)
            self._char_check(text_length, self.limit_footer_text)
            char_count += text_length
        if isinstance(icon_url, str):
            char_count += self.char_count(icon_url)
        self._increment_counter(char_count)
        super().set_footer(text=text, icon_url=icon_url)

    def set_timestamp(self, utc_time: datetime):
        self.timestamp = utc_time

    def set_title(self, text):
        char_count = self.char_count(text)
        self._char_check(char_count, self.limit_title)
        self._increment_counter(char_count)
        self.title = text

    def set_url(self, url):
        char_count = self.char_count(url)
        self._increment_counter(char_count)
        self.url = url

    def speculative_characters_used(self):
        char_length = max(self.count_total_chars, len(self))
        expected_length = char_length + len(self.field_start_chars) + len(self.field_end_chars) + \
                          len(self.field_buffer) + len(self.field_buffer_current)
        expected_length += len(self.field_buffer_continued_name) if self.field_buffer_is_continued else \
            len(self.field_buffer_name)
        return expected_length

    def remaining_characters(self):
        return self.limit_total_char - self.speculative_characters_used()

    def ratio_remaining_characters(self):
        return self.remaining_characters() / self.limit_total_char

    def remaining_fields(self):
        return self.limit_total_fields - self.count_fields

    def ratio_remaining_fields(self):
        return self.remaining_fields() / self.limit_total_fields

    def check_remaining_lower_limits(self, ceiling_characters=0, ceiling_fields=0):
        if self.remaining_characters() <= ceiling_characters or self.remaining_fields() <= ceiling_fields:
            return True
        return False

    def check_remaining_lower_limits_ratio(self, ceiling_characters=0, ceiling_fields=0):
        if self.ratio_remaining_characters() <= ceiling_characters or self.ratio_remaining_fields() <= ceiling_fields:
            return True
        return False

