from unittest import TestCase
import os
from tests.resources import ResourceRoot
import random
import string
import json
import sys
import InsightUtilities
import shutil


class InsightTestBase(TestCase):
    @classmethod
    def tearDownClass(cls):
        InsightUtilities.InsightSingleton.clear_instance_references()

    def setUp(self):
        self.resources = None
        self.resources = ResourceRoot.ResourceRoot.get_path()
        sys.argv = [sys.argv[0]]

    @classmethod
    def get_file_lines_from_abs(self, abs_path, filename):
        with open(os.path.join(abs_path, filename)) as f:
            return f.read().splitlines()

    def get_file_lines(self, filename):
        return self.get_file_lines_from_abs(self.resources, filename)

    @classmethod
    def file_json_from_abs(cls, abs_path, filename):
        with open(os.path.join(abs_path, filename)) as f:
            return json.load(f)

    def file_json(self, filename):
        return self.file_json_from_abs(self.resources, filename)

    @classmethod
    def get_resource_path(cls, *args, path=None):
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

    def random_int(self, min_number, max_number):
        return random.randint(min_number, max_number)

    @classmethod
    def set_sys_args(cls, *args):
        sys.argv = [sys.argv[0]]
        sys.argv.extend(list(args))

    def copy_file_into_cwid(self, path, file):
        shutil.copy(os.path.join(path, file), os.getcwd())

    def remove_file(self, f):
        if os.path.exists(f):
            os.remove(f)

    def append_file(self, file_path, *args):
        with open(file_path, 'a') as f:
            f.writelines(args)
