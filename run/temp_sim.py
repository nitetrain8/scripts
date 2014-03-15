"""

Created by: Nathan Starkweather
Created on: 03/13/2014
Created in: PyCharm Community Edition


"""
from decimal import Decimal
from datetime import timedelta
from math import fsum
from scripts.tpid.tpidmany import full_open_data_report, full_open_eval_steps_report
from scripts.tpid.tpidmany import _debug_tpid_eval_full_scan as debug_scan
from scripts.tpid.tpidmany import tpid_eval_data_scan
from functools import reduce
from operator import mul

__author__ = 'Nathan Starkweather'


# Constant in units of 1/sec(?)
HEAT_DECAY_CONSTANT = Decimal("-0.00006351534757675651529022629111")


def next_temp(tcur, tenv, c=HEAT_DECAY_CONSTANT):
    tdiff = tcur - tenv
    tincr = c * tdiff
    new_t = tcur + tincr
    return new_t


class DecayResult():
    def __init__(self, start_time, end_time, start_pv, end_pv):
        self.end_temp = end_pv
        self.start_temp = start_pv
        self.end_time = end_time
        self.start_time = start_time

    def decay(self):
        """
        @return:
        @rtype: Decimal
        """
        diff = Decimal(self.end_temp - self.start_temp)
        tdiff = self.end_time - self.start_time
        tdiff = Decimal(tdiff.total_seconds()) / 3600
        return diff / tdiff

    def __str__(self):
        return """Tstart: {0} Tend: {1} PVstart: {2} PVend: {3}""".format(self.start_time,
                                                                          self.end_time,
                                                                          self.start_temp,
                                                                          self.end_temp)


def calc_c(rate, temp_diff):
    """
    @rtype : Decimal
    """
    return rate / Decimal(temp_diff)


def calc_ave_c(tests, room_temp):
    """
    @param tests:
    @type tests: list[DecayResult]
    @param room_temp:
    @type room_temp: int | float | Decimal
    @return:
    @rtype:
    """
    all_c = [calc_c(test.decay(), test.start_temp - room_temp) for test in tests]
    ave_c = sum(all_c) / len(all_c)
    assert isinstance(ave_c, Decimal)
    return ave_c

def calc_heats(data, test_list, delay=0):
    """
    @param data: DataReport
    @type data: DataReport
    @param test_list:
    @type test_list: list[scripts.tpid.tpidmany.RampTestResult]
    @return:
    @rtype: list[DecayResult]
    """
    downs = [t for t in test_list if t.start_temp > t.set_point]
    heat_iter = iter(data['TempHeatDutyActual(%)'])
    pv_iter = iter(data['TempPV(C)'])
    #: @type: list[DecayResult]
    heats = []
    for t in downs:
        start = t.start_time + timedelta(minutes=delay)
        start_pv = next(pv for time, pv in pv_iter if time >= start)
        next(_ for time, _ in heat_iter if time >= start)
        end_time = next(time for time, pv in heat_iter if pv)
        end_time, end_pv = next(((time, pv) for time, pv in pv_iter
                                 if ((time - start).total_seconds() >= 1800
                                     or time >= end_time)), end_time)

        # if t.start_temp == 37 and t.set_point == 33:
        #     print((end_time-start).total_seconds())

        d = DecayResult(start, end_time, start_pv, end_pv)
        heats.append(d)
    return heats


def get_stuff():

    data_file = "C:\\Users\\PBS Biotech\\Downloads\\evalfulldata.csv"
    steps_file = "C:\\Users\\PBS Biotech\\Downloads\\evalfullsteps.csv"
    data = full_open_data_report(data_file)
    steps = full_open_eval_steps_report(steps_file)
    test_list = tpid_eval_data_scan(data, steps, 6.5)

    return data, test_list


def find_c(rt=25):

    data, test_list = get_stuff()
    heats = calc_heats(data, test_list)

    # for h in heats:
        # d = calc_c(h.decay(), h.start_temp - 25)
        # print(h.end_time - h.start_time, "%.8f" % h.decay(), round(h.start_temp), d)
        # print((h.end_time-h.start_time).total_seconds() / 60)

    many_c = []
    for delay in range(10, 20):
        heats = calc_heats(data, test_list[:-1], delay)
        c = calc_ave_c(heats, rt)
        # print("Delay: %d" % delay, "ave_c: %s" % str(c))
        many_c.append(c)

    ave_c = sum(many_c) / len(many_c)
    ave_c /= 3600
    # print(ave_c)
    return ave_c


def plot_fourier(start_temp='37.01', c=HEAT_DECAY_CONSTANT):

    from officelib.xllib.xlcom import xlObjs
    start_temp = Decimal(start_temp)
    tcur = start_temp
    rt = 25
    xl, wb, ws, cells = xlObjs("Book2")
    cell_range = cells.Range
    data = []
    for s in range(3600):

        data.append((s, "%.12f" % tcur))
        tcur = next_temp(tcur, rt, c)

    d_len = len(data)
    d_range = cell_range(cells(1, 4), cells(d_len, 5))
    d_range.Value = data


def main():
    data, test_list = get_stuff()
    td = timedelta(minutes=45)
    heatpv = data['TempHeatDutyActual(%)']

    heats = []
    for t in test_list:
        tend = t.end_time
        twait = t.end_time - td
        good = lambda pt: twait <= pt[0] <= tend
        hs = [Decimal(pv) for _, pv in filter(good, heatpv)]
        have = sum(hs) / len(hs)
        heats.append(have)

    for h in heats:
        print(h)
    print("ave", sum(heats) / len(heats))


class TempSim():

    # Degrees C per sec per tcur - tenv
    passive_cooling_rate = Decimal('-0.00004428785379999')

    # Degrees C per sec per % heat duty
    active_heating_rate = Decimal('0.012489')

    # in seconds
    default_increment = Decimal(1)

    def __init__(self, tstart, tenv, heat_duty, cool_rate=None, heat_rate=None):
        """
        @param tstart: start temp
        @type tstart: numbers.Number
        @param tenv: env temp
        @type tenv: numbers.Number
        @param heat_duty: heat duty
        @type heat_duty: numbers.Number
        @param cool_rate: cooling rate constant in degC/sec/dt
        @type cool_rate: numbers.Number
        @param heat_rate: heat rate constant in degC/sec/%heatduty
        @type heat_rate: numbers.Number
        """

        self.start_temp = tstart
        self.current_temp = tstart
        self.env_temp = tenv
        self._env_start_temp = self.env_temp

        self.cool_rate = cool_rate or self.passive_cooling_rate
        self.heat_rate = heat_rate or self.active_heating_rate
        if cool_rate is not None:
            self.passive_cooling_rate = Decimal(cool_rate)
        if heat_rate is not None:
            self.active_heating_rate = Decimal(heat_rate)
        self.seconds = 0
        self.heat_duty = heat_duty

    @property
    def heat_duty(self):
        return self._heat_duty

    @heat_duty.setter
    def heat_duty(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._heat_duty = val

    @property
    def heat_rate(self):
        return self._heat_rate

    @heat_rate.setter
    def heat_rate(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._heat_rate = val

    @property
    def cool_rate(self):
        return self._cool_rate

    @cool_rate.setter
    def cool_rate(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._cool_rate = val

    @property
    def env_temp(self):
        return self._env_temp

    @env_temp.setter
    def env_temp(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._env_temp = val

    @property
    def current_temp(self):
        return self._current_temp

    @current_temp.setter
    def current_temp(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._current_temp = val

    @property
    def seconds(self):
        return self._seconds

    @seconds.setter
    def seconds(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._seconds = val

    def cool_diff(self, seconds=default_increment):
        tdiff = self.current_temp - self.env_temp
        incr = self.passive_cooling_rate * tdiff * seconds
        return incr

    def heat_diff(self, seconds=default_increment):
        tdiff = self.current_temp - self.env_temp
        incr = self.active_heating_rate * tdiff * seconds * self.heat_duty
        return incr

    def step(self, seconds=default_increment):
        cool_diff = self.cool_diff(seconds)
        heat_diff = self.heat_diff(seconds)
        self.current_temp += cool_diff + heat_diff
        self.seconds += seconds
        return self.current_temp

    def __iter__(self):
        # warning, infinite iteration! use break
        return self

    def __next__(self):
        return self.step()

    def iterate(self, n, sec_per_iter=default_increment):
        rv = (self.step(sec_per_iter) for _ in range(n))
        return rv

def main():
    sim = TempSim(25, 20, 50)

    steps = sim.iterate(100000)
    print(sim.current_temp)


if __name__ == '__main__':
    # plot_fourier()
    main()

