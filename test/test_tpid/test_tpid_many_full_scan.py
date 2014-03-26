"""
At the end of the day, the final output of full_scan should be the same
after refactoring.

"""
from itertools import zip_longest
from shutil import rmtree

import unittest
from scripts.tpid.tpidmany import full_scan
from os.path import dirname, join
from xllib.xladdress import cellStr

__author__ = 'PBS Biotech'

curdir = dirname(__file__)
data_dir = join(curdir, "data")

data_input1 = join(data_dir, "full_scan_data_input.csv")
steps_input1 = join(data_dir, "full_scan_steps_input.csv")
full_scan_result1 = join(data_dir, "full_scan_expected_output.xlsx")


class FullTpidManyTest(unittest.TestCase):

    def setUp(self):
        """
        @return:
        @rtype:
        """
        self.data_input = data_input1
        self.steps_input = steps_input1
        outfile = full_scan_result1

        from officelib.xllib.xlcom import xlObjs
        xl, wb, ws, cells = xlObjs(outfile, visible=False)
        self.expected_output = wb.Worksheets("Sheet1").UsedRange.Value2

        wb.Close(False)
        xl.Quit()

    def test_full_scan(self):
        """
        @return:
        @rtype:
        """
        wb = full_scan(self.data_input, self.steps_input, 60)
        xl = wb.Parent

        expected = self.expected_output
        result = wb.Worksheets("Sheet1").UsedRange.Value2

        # currently only interested in data moved to sheet.
        # Chart logic is relatively easy to clean up, and extremely
        # tedious to compare.
        addr = cellStr
        try:
            for r, (exp_row, result_row) in enumerate(zip_longest(result, expected), 1):
                for c, (exp_cell, result_cell) in enumerate(zip_longest(exp_row, result_row), 1):
                    self.assertEqual(exp_cell, result_cell, msg=addr(r, c))
        finally:
            wb.Close(False)
            xl.Quit()


if __name__ == '__main__':
    unittest.main()
