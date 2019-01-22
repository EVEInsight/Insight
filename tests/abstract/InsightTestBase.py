from unittest import TestCase
import os
from tests.resources import ResourceRoot
import random
import string
import json
import sys


class InsightTestBase(TestCase):
    def setUp(self):
        self.resources = None
        self.resources = ResourceRoot.ResourceRoot.get_path()
        sys.argv = [sys.argv[0]]

    def get_file_lines_from_abs(self, abs_path, filename):
        with open(os.path.join(abs_path, filename)) as f:
            return f.read().splitlines()

    def get_file_lines(self, filename):
        return self.get_file_lines_from_abs(self.resources, filename)

    def file_json(self, filename):
        with open(os.path.join(self.resources, filename)) as f:
            return json.load(f)

    def get_resource_path(self, *args, path=None):
        return os.path.join(path if path is not None else ResourceRoot.ResourceRoot.get_path(), *args)

    def set_resource_path(self, *args):
        self.resources = os.path.join(self.resources if self.resources is not None else
                                      ResourceRoot.ResourceRoot.get_path(), *args)

    def iterate_assert_file(self, input_file, assert_file):
        lines_input = self.get_file_lines(input_file) if not isinstance(input_file, list) else input_file
        lines_assert = self.get_file_lines(assert_file) if not isinstance(assert_file, list) else assert_file
        assert len(lines_input) == len(lines_assert)
        counter = 0
        for i in lines_input:
            yield (i, lines_assert[counter])
            counter += 1

    def random_string(self, min_length=1, max_length=5, random_length=False):
        if random_length:
            len = random.randint(min_length, max_length)
        else:
            len = max_length
        return ''.join(random.choice(string.ascii_letters + string.digits) for c in range(len))
