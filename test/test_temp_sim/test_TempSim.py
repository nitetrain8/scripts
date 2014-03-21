"""

Created by: Nathan Starkweather
Created on: 03/20/2014
Created in: PyCharm Community Edition

Module: test_module
Functions: test_functions

"""
import unittest
from os import makedirs
from os.path import dirname, join, exists
from shutil import rmtree

__author__ = 'PBS Biotech'

curdir = dirname(__file__)
test_dir = dirname(curdir)
test_temp_dir = join(test_dir, "temp")
temp_dir = join(test_temp_dir, "temp_dir_path")
test_input = join(curdir, "test_input")


def setUpModule():
    try:
        makedirs(temp_dir)
    except FileExistsError:
        pass


def tearDownModule():
    try:
        rmtree(temp_dir)
    except FileNotFoundError:
        pass


from scripts.run.temp_sim import TempSim


class TestFastIteration(unittest.TestCase):

    def __init__(self, methodName='runTest'):

        super().__init__(methodName)
        self.addTypeEqualityFunc(TempSim, self.assertTempSimEqual)

    @classmethod
    def setUpClass(cls):
        """
        @return:
        @rtype:
        """
        cls.init_args = (
            (25, 20, 7),  # heating
            (37, 20, 0)   # cooling
        )

    def assertTempSimEqual(self, exp, res, msg=None):
        """
        @param exp:
        @type exp: TempSim
        @param res:
        @type res: TempSim
        @param msg: str | None
        @type msg: str | None
        @return:
        @rtype:
        """

        assertEqual = self.assertEqual

        assertEqual(exp.current_temp, res.current_temp)
        assertEqual(exp.heat_duty, res.heat_duty)
        assertEqual(exp.passive_cooling_rate, res.passive_cooling_rate)
        assertEqual(exp.active_heating_rate, res.active_heating_rate)
        assertEqual(exp.seconds, res.seconds)
        assertEqual(exp.env_temp, res.env_temp)

    def test_iterate(self):
        """
        @return: None
        @rtype: None
        """

        for args in self.init_args:
            exp_sim = TempSim(*args)
            test_sim = TempSim(*args)

            _s = exp_sim.step
            n = 100000
            exp_steps = [_s() for _ in range(n)]
            res_steps = test_sim.iterate(n)

            self.assertEqual(exp_steps, res_steps)
            self.assertEqual(exp_sim, test_sim)

    def test_quiet_iter(self):
        """
        @return:
        @rtype:
        """

        for args in self.init_args:

            exp_sim = TempSim(*args)
            test_sim = TempSim(*args)
            _s = exp_sim.step
            n = 100000

            for _ in range(n):
                _s()

            test_sim.quietiter(n)

            self.assertEqual(exp_sim, test_sim)

            # test quiet step while we're here
            _s()
            test_sim.quietstep()

            self.assertEqual(exp_sim, test_sim)


if __name__ == '__main__':
    unittest.main()
