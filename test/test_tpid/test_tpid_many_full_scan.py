"""
At the end of the day, the final output of full_scan should be the same
after refactoring.

"""
from shutil import rmtree

import unittest
from scripts.tpid.tpidmany import full_scan
from os.path import dirname, join

__author__ = 'PBS Biotech'

curdir = dirname(__file__)
data_dir = join(curdir, "data")

data_input1 = join(data_dir, "full_scan_data_input.csv")
steps_input1 = join(data_dir, "full_scan_steps_input.csv")
full_scan_result1 = join(data_dir, "full_scan_expected_output.xlsx")


class FullTpidManyTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        @return:
        @rtype:
        """
        cls.data_input = data_input1
        cls.steps_input = steps_input1
        cls.temp_dir = join(dirname(curdir), "temp", "tpid_full_scan_temp")
        outfile = full_scan_result1

        from officelib.xllib.xlcom import xlObjs
        cls.xl, cls.wb, cls.ws, cls.cells = xlObjs(outfile, visible=False, verbose=False)
        cls.expected_output = cls.wb.Worksheets("Sheet1").UsedRange.Value2

        cls.wb.Close(False)
        cls.xl.Quit()
        del cls.wb
        del cls.xl

    def test_full_scan(self):
        """
        @return:
        @rtype:
        """
        self.wb = full_scan(self.data_input, self.steps_input, 60)
        self.xl = self.wb.Parent

        result_output = self.wb.Worksheets("Sheet1").UsedRange.Value2

        # currently only interested in data moved to sheet.
        # Chart logic is relatively easy to clean up, and extremely
        # tedious to compare.

        for exp_line, res_line in zip(self.expected_output, result_output):
            self.assertEqual(exp_line, res_line)

    @classmethod
    def tearDownClass(cls):
        """
        Close excel, wb instances
        @return:
        @rtype:
        """
        try:
            cls.cells = None
            cls.ws = None
            cls.wb = None

            for wb in cls.xl.Workbooks:
                try:
                    wb.Close(False)
                except:
                    pass
            cls.xl.Quit()
            cls.xl = None
        except:
            try:
                 cls.xl.Visible = True
            except:
                pass

        try:
            rmtree(cls.temp_dir)
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    unittest.main()
