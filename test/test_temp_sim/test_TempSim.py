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
from decimal import Decimal as D

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


class TempSimTestBase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.addTypeEqualityFunc(TempSim, self.assertTempSimEqual)

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
        assertEqual(exp.cooling_constant, res.cooling_constant)
        assertEqual(exp.heating_constant, res.heating_constant)
        assertEqual(exp.seconds, res.seconds)
        assertEqual(exp.env_temp, res.env_temp)


class TestFastIteration(TempSimTestBase):


    @classmethod
    def setUpClass(cls):
        """
        @return:
        @rtype:
        """
        super().setUpClass()
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
        assertEqual(exp.cooling_constant, res.cooling_constant)
        assertEqual(exp.heating_constant, res.heating_constant)
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
            n = 10000
            exp_steps = [_s() for _ in range(n)]
            res_steps = test_sim.iterate(n)

            self.assertEqual(exp_steps, res_steps)
            self.assertEqual(exp_sim, test_sim)

            # repeat the same thing to ensure iterate works
            # on subsequent calls.
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
            n = 10000

            for _ in range(n):
                _s()

            test_sim.quietiter(n)
            self.assertEqual(exp_sim, test_sim)

            # test quiet step while we're here
            _s()
            test_sim.quietstep()
            self.assertEqual(exp_sim, test_sim)

            # repeat the same thing to ensure iterate works
            # on subsequent calls.
            for _ in range(n):
                _s()

            test_sim.quietiter(n)
            self.assertEqual(exp_sim, test_sim)

            # test quiet step while we're here
            _s()
            test_sim.quietstep()
            self.assertEqual(exp_sim, test_sim)


class TestRampDownAccuracy(TempSimTestBase):

    @classmethod
    def setUpClass(cls):
        """
        @return:
        @rtype:
        """
        super().setUpClass()

        testfile = test_input + "\\rampdownrealishdata.csv"

        with open(testfile, 'r') as f:
            f.readline()
            data = list(zip(*[line.split(',') for line in f.read().splitlines()]))

        time, pvs = data

        time = map(D, time)
        pvs = map(D, pvs)

        cls.decay_data = tuple(zip(time, pvs))

    def test_decay_accuracy(self):
        """
        @return:
        @rtype:
        """

        # Known values from excel analysis of data
        start_temp = D('37.115')
        env_temp = 19
        heat_duty = 0

        sim = TempSim(start_temp, env_temp, heat_duty)
        time = D(0)
        temp = sim.current_temp

        # ensuring an accurate model is trickly.
        # for now, assume that if we stay +/- 0.1 degree,
        # we're doing ok.

        diff_limit = D('0.08')
        diffs = []
        for sec_elapsed, pv in self.decay_data:

            # iterate until elapsed time
            step = sim.step
            while time < sec_elapsed:
                time, temp = step()

            diff = pv - temp
            abs_diff = abs(diff)
            diffs.append(abs_diff)
            self.assertLess(abs_diff, diff_limit)


if __name__ == '__main__':
    unittest.main()
