"""

Created by: Nathan Starkweather
Created on: 02/24/2014
Created in: PyCharm Community Edition


"""
from shutil import rmtree

__author__ = 'Nathan Starkweather'

import unittest
import scripts.tpid.tpidmany as tpidmany
import scripts.test.test_tpid.test_setup as tpid_setup
from os import makedirs
from os.path import dirname, join

curdir = dirname(__file__)
test_dir = dirname(curdir)
data_dir = join(curdir, "data")
temp_dir = join(test_dir, "temp", "tpid_temp")


def copy_list1(to_copy):
    list_iter = iter(to_copy)
    next(list_iter)
    return [line.copy() for line in list_iter]


# noinspection PyProtectedMember
class TestStepTests(tpid_setup.TPIDUnittest):

    def setUp(self):
        """
        @return:
        @rtype:
        """
        super().setUp()
        try:
            makedirs(temp_dir)
        except FileExistsError:
            pass

        self.steps_report1 = join(data_dir, "full_scan_steps_input.csv")
        self.data_report1 = join(data_dir, "full_scan_data_input.csv")

    def test_extract_raw_steps(self):
        """
        @return:
        @rtype:
        """

        extract_raw_steps = tpidmany.extract_raw_steps

        expected_extracted_steps = tpid_setup.steps_report1_expected_lines[1:]

        result = extract_raw_steps(self.steps_report1)
        for exp_line, res_line in zip(expected_extracted_steps, result):
            self.assertEqual(exp_line, res_line)

    def test_extract_test_steps(self):
        """
        @return:
        @rtype:
        """

        extract_test_steps = tpidmany.extract_test_steps

        steps = copy_list1(tpid_setup.steps_report1_expected_lines)
        expected_extracted_tests = tpid_setup.steps_report1_expected_test_steps
        result = extract_test_steps(steps)

        for exp_line, result_line in zip(expected_extracted_tests, result):
            self.assertEqual(exp_line, result_line)

    def test_parse_test_dates(self):
        """
        test parse_test_dates function
        @return:
        @rtype:
        """

        parse_test_dates = tpidmany.parse_test_dates
        expected = tpid_setup.steps_report1_datetimes
        input_tests = tpid_setup.steps_report1_expected_test_steps

        assertEqual = self.assertEqual
        result = parse_test_dates(input_tests)

        # Slower on failures, but just as fast on passes.
        # Would rather fail slowly with an easy to understand
        # error message.
        try:
            assertEqual(expected, result)
        except self.failureException:
            for in_line, exp_line, res_line in zip(input_tests, expected, result):
                try:
                    assertEqual(exp_line, res_line)
                except self.failureException:
                    for in_str, exp_dt, res_dt in zip(in_line, exp_line, res_line):
                        assertEqual(exp_dt, res_dt, msg="Invalid result from input str '%s'" % in_str)

    def tearDown(self):
        """
        @return:
        @rtype:
        """
        try:
            rmtree(temp_dir)
        except FileNotFoundError:
            pass



if __name__ == '__main__':
    unittest.main()
