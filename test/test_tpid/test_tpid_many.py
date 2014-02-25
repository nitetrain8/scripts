"""

Created by: Nathan Starkweather
Created on: 02/24/2014
Created in: PyCharm Community Edition


"""
from shutil import rmtree

__author__ = 'Nathan Starkweather'

import unittest
from scripts.tpid.tpidmany import find_step_tests
from os import makedirs
from os.path import dirname, join

curdir = dirname(__file__)
test_dir = dirname(curdir)
temp_dir = join(test_dir, "temp", "tpid_temp")


class TestStepTests(unittest.TestCase):

    def setUp(self):
        """
        @return:
        @rtype:
        """
        try:
            makedirs(temp_dir)
        except FileExistsError:
            pass

        self.temp_dir = temp_dir





    def tearDown(self):
        """
        @return:
        @rtype:
        """
        try:
            rmtree(self.temp_dir)
        except FileNotFoundError:
            pass
