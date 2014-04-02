"""

Created by: Nathan Starkweather
Created on: 03/20/2014
Created in: PyCharm Community Edition

Module: test_module
Functions: test_functions

"""
import unittest
from os import makedirs
from os.path import dirname, join
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


from scripts.run.temp_sim import TempSim, PIDController


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
        assertEqual(exp.cool_rate, res.cool_rate)
        assertEqual(exp.heat_rate, res.heat_rate)
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
        assertEqual(exp.cool_rate, res.cool_rate)
        assertEqual(exp.heat_rate, res.heat_rate)
        assertEqual(exp.seconds, res.seconds)
        assertEqual(exp.env_temp, res.env_temp)

    def test_iterate(self):
        """
        @return: None
        @rtype: None
        """

        assertEqual = self.assertEqual

        for args in self.init_args:
            exp_sim = TempSim(*args, leak_const=0)
            test_sim = TempSim(*args, leak_const=0)

            step = exp_sim.step
            n = 10000
            exp_steps = [step() for _ in range(n)]
            res_steps = test_sim.iterate(n)

            # unloop assert otherwise hangup caused
            # by trying to process too long of a diff in
            # repr string

            for step_no, (exp_step, res_step) in enumerate(zip(exp_steps, res_steps)):
                assertEqual(exp_step, res_step, step_no)

            assertEqual(exp_sim, test_sim)

            # repeat the same thing to ensure iterate works
            # on subsequent calls.
            exp_steps = [step() for _ in range(n)]
            res_steps = test_sim.iterate(n)

            for step_no, (exp_step, res_step) in enumerate(zip(exp_steps, res_steps)):
                assertEqual(exp_step, res_step, step_no)
            assertEqual(exp_sim, test_sim)

    def test_quiet_iter(self):
        """
        @return:
        @rtype:
        """

        for args in self.init_args:

            exp_sim = TempSim(*args, leak_const=0)
            test_sim = TempSim(*args, leak_const=0)
            step = exp_sim.step
            n = 10000

            for _ in range(n):
                step()

            test_sim.quietiter(n)
            self.assertEqual(exp_sim, test_sim)

            # test quiet step while we're here
            step()
            test_sim.quietstep()
            self.assertEqual(exp_sim, test_sim)

            # repeat the same thing to ensure iterate works
            # on subsequent calls.
            for _ in range(n):
                step()

            test_sim.quietiter(n)
            self.assertEqual(exp_sim, test_sim)

            # test quiet step while we're here
            step()
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

Decimal = D


class SimArgs():

    def __init__(self, start_temp, env_temp, heat_duty,
                 cool_constant=TempSim.DEFAULT_COOL_CONSTANT,
                 heat_constant=TempSim.DEFAULT_HEAT_CONSTANT,
                 delay=0, step_increment=0, nsteps=3000):

        self.delay = delay
        self.nsteps = nsteps
        self.step_increment = step_increment
        self.heat_rate = heat_constant
        self.cool_rate = cool_constant
        self.heat_duty = heat_duty
        self.env_temp = env_temp
        self.start_temp = start_temp

    @property
    def start_temp(self):
        return self._start_temp

    @start_temp.setter
    def start_temp(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._start_temp = val

    @property
    def env_temp(self):
        return self._env_temp

    @env_temp.setter
    def env_temp(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._env_temp = val

    @property
    def heat_duty(self):
        return self._heat_duty

    @heat_duty.setter
    def heat_duty(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._heat_duty = val

    @property
    def cool_rate(self):
        return self._cooling_constant

    @cool_rate.setter
    def cool_rate(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._cooling_constant = val

    @property
    def heat_rate(self):
        return self._heating_constant

    @heat_rate.setter
    def heat_rate(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._heating_constant = val

    @property
    def step_increment(self):
        return self._step_increment

    @step_increment.setter
    def step_increment(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._step_increment = val

    def get_args(self):
        return (self.start_temp, self.env_temp, self.heat_duty,
                self.cool_rate, self.heat_rate, self.delay)

    def get_step(self):
        return self.nsteps, self.step_increment


class RegressionTest(TempSimTestBase):

    """This class's use of 'SimArgs' to hold test info is a mess.
    Sorry. Use lists or hard code test, next time."""

    @classmethod
    def setUpClass(cls):
        """
        @return:
        @rtype:
        """

        cls.sim_args = [
            SimArgs(25, 19, 7),
            SimArgs(37, 19, 0),
            SimArgs(25, 19, 7, '-0.0004'),
            SimArgs(25, 19, 7, '-0.0007'),
            SimArgs(25, 19, 7, "-0.0004", "0.0001"),
            SimArgs(25, 19, 7, '-0.0007', '0.00014'),
            SimArgs(25, 19, 7, step_increment=3)
        ]

        cls.regression_folder = test_input + '\\regression'
        cls.regression_file = test_input + '\\regression\\regression_op.pickle'
        from pickle import load

        with open(cls.regression_file, 'rb') as f:
            #: @type: list[SimArgs, list[D, D]]
            cls.exp = load(f)

        # cls.exp[2][0].heat_duty = 0
        cls.cmp_prec = 8

    def test_regression_output(self):
        """
        @return:
        @rtype:
        """

        self.addTypeEqualityFunc(D, self.assertRoundDecimalEqual)
        assertTupleEqual = self.assertTupleEqual
        # results = []
        for args, expected in self.exp:
            args.delay = 0
            init_args = args.get_args()
            nsteps, step_size = args.get_step()
            sim = TempSim(*init_args)

            if step_size:
                result = sim.iterate(nsteps, step_size)
            else:
                result = sim.iterate(nsteps)

            # assertEqual(expected, result)

            for exp_step, r_step in zip(expected, result):
                assertTupleEqual(exp_step, r_step, init_args)

            # results.append((args, result))

            # use SimArgs as a dummy TempSim to compare.
            # Fill in missing attrs using result data
            args.seconds, args.current_temp = result[-1]

            # noinspection PyTypeChecker
            self.assertTempSimEqual(args, sim)

        # from pysrc.snippets import safe_pickle
        # safe_pickle(results, self.regression_file)

    def assertRoundDecimalEqual(self, exp, result, msg=None):
        """
        @param exp:
        @type exp:
        @param result:
        @type result:
        @param msg:
        @type msg:
        @return:
        @rtype:
        """
        prec = self.cmp_prec
        round_exp = round(exp, prec)
        round_result = round(result, prec)

        if not round_exp == round_result:
            self.fail(msg)

    def run_process(self, sim, pid, n):
        pv = sim.current_temp
        pid.auto_mode(pv)
        result = []
        ap = result.append
        for _ in range(n):
            hd = pid.step_output(pv)
            t, pv = sim.step_heat(pv)
            ap((t, pv, hd))
        return result

    def test_delay_buf_sink(self):
        """
        make sure that delay of 0 and heat sink of 100% leak rate
        both result in identical results as old thingy.
        @return:
        @rtype:
        """
        ref = self.regression_folder + '\\ref_delay1.pickle'

        from pickle import load as pload

        with open(ref, 'rb') as f:
            exp = pload(f)

        sim = TempSim(28, 19, 0, delay=0)
        pid = PIDController(37, 40, 30, ideal=False)

        result = self.run_process(sim, pid, 9500)

        for exp_pt, res_pt in zip(exp, result):
            self.assertEqual(exp_pt, res_pt)

        # sim = TempSim(28, 19, 0, delay=0)
        # pid = PIDController(37, 40, 30)

        # result = self.run_process(sim, pid, 9500)

        # from pysrc.snippets import safe_pickle
        # safe_pickle(result, test_input + '\\regression\\ref_delay.pickle')


if __name__ == '__main__':
    unittest.main()
