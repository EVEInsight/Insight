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
        self.count_fields = 0
        self.count_total_chars = 0

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

    def add_field(self, *, name, value, inline=True):
        char_count = 0

        name_length = self.char_count(name)
        self._char_check(name_length, self.limit_field_name)
        char_count += name_length

        value_length = self.char_count(name)
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



