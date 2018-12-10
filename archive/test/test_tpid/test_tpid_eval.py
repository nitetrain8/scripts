"""

Created by: Nathan Starkweather
Created on: 03/07/2014
Created in: PyCharm Community Edition

Module: test_module
Functions: test_functions

"""
import unittest
from datetime import datetime
from itertools import zip_longest
from os import makedirs
from os.path import dirname, join
from shutil import rmtree

from pbslib.batchreport import DataReport

import scripts.tpid.tpidmany as tpidmany
from scripts.test.test_tpid.test_setup import TPIDUnittest
from xllib.xladdress import cellStr
from xllib.xlcom import xlObjs

__author__ = 'PBS Biotech'

curdir = dirname(__file__)
test_dir = dirname(curdir)
test_temp_dir = join(test_dir, "temp")
temp_dir = join(test_temp_dir, "temp_dir_path")
test_input = join(curdir, "data")


class TestEvalSteps(TPIDUnittest):

    xl_need_closing = []

    @classmethod
    def setUpClass(cls):
        """
        @return: None
        @rtype: None
        """
        try:
            makedirs(temp_dir)
        except FileExistsError:
            pass

        cls.data_csv = join(test_input, 'eval_data_input.csv')
        cls.data_report = DataReport(cls.data_csv)
        cls.steps_csv = join(test_input, 'eval_steps_input.csv')
        cls.exp_full_result = join(test_input, 'eval_full_scan_result.xlsx')

        cls.xl_need_closing = []

    @unittest.skip("Test not yet written")
    def test_tpid_eval_data_scan(self):
        """
        @return: None
        @rtype: None
        """

        steps = tpidmany.tpid_eval_steps_scan(self.steps_csv)
        data = self.data_report

        # Todo
        result = tpidmany.tpid_eval_data_scan(data, steps)

    def test_tpid_eval_full_scan(self):
        """
        Test the full scan

        @return:
        @rtype:
        """
        data = self.data_csv
        steps = self.steps_csv

        res_wb = tpidmany.tpid_eval_full_scan(data, steps, 7)
        self.xl_need_closing.append(res_wb.Parent)

        xl, wb, ws, cells = xlObjs(self.exp_full_result, visible=False)
        self.xl_need_closing.append(xl)

        result = res_wb.Worksheets(1).UsedRange.Value2
        expected = wb.Worksheets(1).UsedRange.Value2

        # Include excel cell address of any mismatch
        # start = 1 for 1 based index
        addr = cellStr
        for r, (exp_row, result_row) in enumerate(zip_longest(result, expected), 1):
            for c, (exp_cell, result_cell) in enumerate(zip_longest(exp_row, result_row), 1):
                self.assertEqual(exp_cell, result_cell, msg=addr(r, c))

    def test_tpid_eval_steps_scan(self):
        """
        @return:
        @rtype:
        """

        scan = tpidmany.tpid_eval_steps_scan
        result = scan(self.steps_csv)

        # Todo
        for start, end in result:
            self.assertIsInstance(start, datetime)
            self.assertIsInstance(end, datetime)

    @classmethod
    def tearDownClass(cls):
        """
        @return: None
        @rtype: None
        """
        try:
            rmtree(temp_dir)
        except FileNotFoundError:
            pass
        e = None
        for xl in cls.xl_need_closing:
            # xl.Visible = True
            for wb in xl.Workbooks:
                try:
                    wb.Close(False)
                except:
                    pass
            try:
                xl.Quit()
            except Exception as e:
                try:
                    xl.Visible = True
                except:
                    pass

        del cls.xl_need_closing

        if e:
            raise e

if __name__ == '__main__':
    unittest.main()
