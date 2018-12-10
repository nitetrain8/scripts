"""

Created by: Nathan Starkweather
Created on: 03/13/2014
Created in: PyCharm Community Edition


"""
from decimal import Decimal
D = Decimal
from datetime import timedelta
from itertools import repeat


from collections import deque

__author__ = 'Nathan Starkweather'

exhaust = deque(maxlen=0).extend

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
        tdiff = Decimal(tdiff.total_seconds())
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
                                 if time >= end_time), end_time)

        # if t.start_temp == 37 and t.set_point == 33:
        #     print((end_time-start).total_seconds())

        d = DecayResult(start, end_time, start_pv, end_pv)
        heats.append(d)
    return heats


def get_stuff():
    from scripts.tpid.tpidmany import full_open_data_report, full_open_eval_steps_report
    from scripts.tpid.tpidmany import tpid_eval_data_scan

    data_file = "C:\\Users\\PBS Biotech\\Downloads\\evalfulldata.csv"
    steps_file = "C:\\Users\\PBS Biotech\\Downloads\\evalfullsteps.csv"
    data = full_open_data_report(data_file)
    steps = full_open_eval_steps_report(steps_file)
    test_list = tpid_eval_data_scan(data, steps, 6.5)

    return data, test_list


def find_c(rt=25):

    data, test_list = get_stuff()
    # heats = calc_heats(data, test_list)

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


def print_ave_heats():
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


class DelayBuffer(deque):

    def __init__(self, delay=30, startvalue=0):
        # No maxlen- let potential delay size
        # be dynamicly determinable by caller
        super().__init__(repeat(D(startvalue), delay + 1))

    def cycle(self, hd, rot=deque.rotate):
        self[0] = hd
        rot(self, 1)
        return self[0]


class HeatSink():

    dbg_buf = []

    def __init__(self, leak_const=D('20')):
        """
        @param leak_const:
        @type leak_const: int | Decimal
        """
        if leak_const <= -1:
            raise ValueError("Can't use leak constant <= -1")
        self.current = D(0)
        self.leak_rate = D(1) / D(1 + D(leak_const))

    def step(self, val):
        self.current += val
        leak = self.current * self.leak_rate
        self.current -= leak
        return leak


# noinspection PyRedeclaration
class TempSim():

    # Degrees C per sec per tcur - tenv
    # Degrees C per sec per % heat duty

    # DEFAULT_COOL_CONSTANT = Decimal('-0.00004679011328')
    # DEFAULT_HEAT_CONSTANT = Decimal('0.0001140')

    DEFAULT_COOL_CONSTANT = Decimal('-0.00004')
    DEFAULT_HEAT_CONSTANT = Decimal('0.000097456')

    # archived constants
    # cool_rate = Decimal('-0.00004428785379999')
    # cool_rate = Decimal('-0.0000615198895')
    # cool_rate = Decimal('-0.00011')
    # heat_rate = Decimal('0.00010')

    # in seconds
    default_increment = Decimal(1)

    def __init__(self, start_temp=28, env_temp=19, heat_duty=0,
                 cool_constant=DEFAULT_COOL_CONSTANT, heat_constant=DEFAULT_HEAT_CONSTANT,
                 delay=0, leak_const=0):
        """
        @param start_temp: start temp
        @type start_temp: int | float | decimal.Decimal
        @param env_temp: env temp
        @type env_temp: int | float | decimal.Decimal
        @param heat_duty: heat duty
        @type heat_duty: int | float | decimal.Decimal
        @param cool_constant: cooling rate constant in degC/(sec*dt)
        @type cool_constant: int | float | decimal.Decimal
        @param heat_constant: heat rate constant in degC/(sec*%heatduty)
        @type heat_constant: int | float | decimal.Decimal
        """

        self.start_temp = start_temp
        self.current_temp = start_temp
        self.env_temp = env_temp

        self.cool_rate = cool_constant
        self.heat_rate = heat_constant

        self.seconds = 0
        self.heat_duty = heat_duty

        self.delay = DelayBuffer(delay, heat_duty).cycle
        if leak_const == 0:
            # Shortcut to save some computation time.
            self.sink_step = lambda x: x
        elif leak_const < 0:
            raise ValueError("Leak constant must be 0 or greater")
        else:
            self.sink_step = HeatSink(leak_const).step

    # Properties used to simplify the process of ensuring that all internal
    # numeric processing is done via Decimal. Use setters to automatically
    # check type of newly assigned value. Use getters because you can't
    # use a setter by itself.

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
    def minutes(self):
        return self._seconds / 60

    @property
    def hours(self):
        return self._seconds / 3600

    @property
    def days(self):
        return self._seconds / 86400

    @property
    def seconds(self):
        return self._seconds

    @seconds.setter
    def seconds(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._seconds = val

    def cool_diff(self, seconds=default_increment):
        tdiff = self._current_temp - self._env_temp
        incr = self._cool_rate * tdiff * seconds
        return incr

    def heat_diff(self, seconds=default_increment):
        incr = self._heat_rate * seconds * self._heat_duty
        incr = self.sink_step(incr)
        return incr

    def step(self, seconds=default_increment):
        """
        @type seconds: decimal.Decimal
        @return: decimal.Decimal
        @rtype: (decimal.Decimal, decimal.Decimal)
        """
        return self._step(seconds)

    def _step(self, seconds):
        """
        @type seconds: decimal.Decimal
        @return: decimal.Decimal
        @rtype: (decimal.Decimal, decimal.Decimal)
        """

        tdiff = self._current_temp - self._env_temp
        cool_diff = self._cool_rate * tdiff * seconds

        incr = self._heat_rate * seconds * self._heat_duty
        heat_diff = self.sink_step(incr)

        self._current_temp += cool_diff + heat_diff
        self._seconds += seconds

        return self.seconds, self.current_temp

    def __iter__(self):
        # warning, infinite iteration! use break
        return self

    def __next__(self):
        return self.step()

    def iterate(self, n, sec_per_iter=default_increment):

        # optimize slightly, similar methodology to quietiter()
        # see quietiter() for details/assumptions
        sec_per_iter = Decimal(sec_per_iter)

        naive_heat_per_iter = self.heat_diff(sec_per_iter)
        naive_cool_const = self._cool_rate * sec_per_iter
        env_temp = self.env_temp

        ct = self.current_temp
        sec = self.seconds
        steps = []; append = steps.append
        # delay = self.delay

        for _ in range(n):
            ct += naive_heat_per_iter + naive_cool_const * (ct - env_temp)
            sec += sec_per_iter
            append((sec, ct))

        self.current_temp = ct
        self.seconds = sec

        return steps

    def __repr__(self):
        # noinspection PyStringFormat
        msg = """Start: %.1f HeatDuty: %.1f Current: %.3f Elapsed %d""" % (self.start_temp,
                                                                        self.heat_duty,
                                                                        self.current_temp,
                                                                        self.seconds)
        return msg

    __str__ = __repr__

    def quietstep(self, seconds=default_increment):
        self._step(seconds)

    def quietiter(self, n, sec_per_iter=default_increment):
        # inline step() and cool diff/heat diff for speed
        # If the increment and heat duty never change, then
        # heat per iter is constant, so we only need calculate it once.
        # cool_per_sec with constant increment only needs to
        # recalculate tdiff.

        # ASSUMPTIONS:
        # constant sec_per_iter
        # constant heating and cooling constants
        # constant env temperature
        # constant heat duty

        sec_per_iter = Decimal(sec_per_iter)

        heat_per_iter = self.heat_diff(sec_per_iter)
        cool_const = self._cool_rate * sec_per_iter

        env_temp = self.env_temp
        current_temp = self.current_temp

        for _ in range(n):
            cool_diff = cool_const * (current_temp - env_temp)
            current_temp += cool_diff + heat_per_iter

        self.seconds += n * sec_per_iter
        self.current_temp = current_temp

    def step_till(self, temp):
        if not isinstance(temp, Decimal):
            temp = Decimal(temp)
        if self.current_temp > temp:
            return
        next(v for v in self if v[1] > temp)

    def step_heat(self, hd, sec=default_increment):
        hd = self.delay(hd)
        self.heat_duty = hd
        return self._step(sec)


class PIDController():

    AUTO_MODE = 1
    OFF_MODE = 0

    def __init__(self, set_point=37, pgain=40, itime=33, dtime=0, automax=50,
                 auto_min=0, out_high=100, out_low=0, l=1, b=1, ideal=True):
        """
        @type set_point: int | float
        @type pgain: int | float
        @type itime: int | float
        @type dtime: int | float
        @type automax: int | float
        @param auto_min: int | float
        @type auto_min: int | float
        @type out_high: int | float
        @type out_low: int | float
        @type l: int | float
        @type b: int | float
        @return:
        @rtype:
        """
        self.auto_min = D(auto_min)
        self.out_low = out_low
        self.out_high = out_high
        self.out_range = D(out_high - out_low) / 2
        self.set_point = D(set_point)
        self.automax = Decimal(automax)
        self.pgain = D(pgain)
        self.itime = D(itime)
        self.oneoveritime = 1 / self.itime  # used to calc accumulated_error time
        self.dtime = D(dtime)
        self.ideal = ideal

        self.L = l
        self.B = b

        zero = Decimal(0)

        self.accumulated_error = zero
        self.seconds = zero
        self.current_output = zero
        self.bump = zero
        self.last_error = zero
        self.last_pv = zero
        self.lastlastpv = zero

    def off_to_auto(self, pv):
        """
        Turn the reactor on in auto mode at pv, aka
        calculate the bump.

        @param pv: current process temp to use for bumpless xfer calculation
        @type pv: int | float | decimal.Decimal
        """
        self.man_to_auto(0, pv)

    def man_to_auto(self, hd, pv):
        """
        @param hd: current heat duty, for bumpless xfer calculation
        @type hd: int | float | decimal.Decimal
        @param pv: current process temp to use for bumpless xfer calculation
        @type pv: int | float | decimal.Decimal
        """
        err = self.set_point - pv
        uk0 = self.pgain * err
        self.bump = hd - uk0
        #print("hd %.2f, pv %d, bump %.2f" % (hd, pv, self.bump))

    def reset(self):
        self.bump = 0
        self.accumulated_error = 0

    @property
    def bump(self):
        return self._bump

    @bump.setter
    def bump(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._bump = val

    @property
    def oneoveritime(self):
        return self._oneoveritime

    @oneoveritime.setter
    def oneoveritime(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._oneoveritime = val

    @property
    def pgain(self):
        return self._pgain

    @pgain.setter
    def pgain(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._pgain = val

    @property
    def itime(self):
        return self._itime

    @itime.setter
    def itime(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._itime = val
        self.oneoveritime = 1 / self._itime

    @property
    def dtime(self):
        return self._dtime

    @dtime.setter
    def dtime(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._dtime = val

    @property
    def set_point(self):
        return self._set_point

    @set_point.setter
    def set_point(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._set_point = val

    @property
    def accumulated_error(self):
        return self._accumulated_error

    @accumulated_error.setter
    def accumulated_error(self, val, D=Decimal, isinst=isinstance):
        if not isinst(val, D):
            val = D(val)
        self._accumulated_error = val

    def process_error(self, pv, dt):
        """
        @type pv: decimal.Decimal
        @type dt: decimal.Decimal
        @return:
        @rtype:
        """

        e_t = self.set_point - pv
        self.accumulated_error += dt * e_t
        self.seconds += dt
        self.last_error = e_t
        self.last_pv = self.lastlastpv
        self.lastlastpv = pv
        return e_t

    def calc_output(self, error, pv):
        """
        @param error: the error sp - pv
        @param pv: current process value, used to calc deriv
                    action and avoid massive kicks at SP change
        @type error: decimal.Decimal
        @type pv: decimal.Decimal
        @return: the heater duty output in %
        @rtype: decimal.decimal
        """

        Ui = self._oneoveritime * self._accumulated_error

        # Trapezoidal integration
        # out_range = self.out_range
        # Ui = self._oneoveritime * self._accumulated_error / (1 + (10 * error * error) / (out_range * out_range))
        # print(pv - self.last_pv)

        Ud = self._dtime * (pv - self.last_pv)

        if self.ideal:
            Uk = self._bump + self._pgain * (error + Ui + Ud)
        else:
            Uk = self._bump + self._pgain * error + Ui + Ud

        if Uk > self.automax:
            Uk = self.automax
        elif Uk < self.auto_min:
            Uk = self.auto_min

        return Uk

    def step_output(self, pv, dt=D(1)):
        """
        Side effects: increases accumulated error
        @param pv: pv
        @type pv: Decimal
        @param dt: time difference
        @type dt: Decimal
        @return: new process output
        @rtype: Decimal
        """
        e_t = self.process_error(pv, dt)
        output = self.calc_output(e_t, pv)
        self.current_output = output
        return output

    def __repr__(self):
        return "Output: %.2f Pgain: %.1f Itime: %.2f AccumError: %.4f" % (self.current_output,
                                                                          self.pgain,
                                                                          self.itime,
                                                                          self.accumulated_error
                                                                          )
    __str__ = __repr__


def est_tp(hd1, hd2):
    sim = TempSim(20, 20, hd1)
    sim.quietiter(200000)
    temp1 = sim.current_temp
    print('temp1', temp1)
    print(sim)
    sim.heat_duty = hd2
    bump_steps = sim.iterate(200000)
    temp2 = sim.current_temp
    dt = temp2 - temp1
    t63 = temp1 + dt * Decimal('0.63')
    tend = next(i for i, t in enumerate(bump_steps, start=1) if t[1] > t63)
    del bump_steps
    _l = list(locals().items())
    print("After Simulation Run:")
    for k, v in _l:
        print(k, v)
    return tend


def est_kp(hd1, hd2):
    hd1 = Decimal(hd1)
    hd2 = Decimal(hd2)
    sim = TempSim(25, 20, hd1)
    sim.quietiter(500000)
    temp1 = sim.current_temp
    sim.heat_duty = hd2
    sim.quietiter(500000)
    temp2 = sim.current_temp

    dPV = temp2 - temp1
    dCO = hd2 - hd1

    return dPV / dCO


def est_both(hd1, hd2, st=D('37.115'), n=500000):

    hd1 = Decimal(hd1)
    hd2 = Decimal(hd2)
    sim = TempSim(st, 19, hd1, D('-0.00004679011328'))

    sim.quietiter(n)
    temp1 = sim.current_temp
    tstart = sim.seconds
    sim.heat_duty = hd2

    bump_steps = sim.iterate(n)
    temp2 = sim.current_temp
    dt = temp2 - temp1
    t63 = temp1 + dt * Decimal('0.63')

    if dt > 0:
        cmp = t63.__lt__
    else:
        cmp = t63.__gt__

    tend = next(i for i, t in bump_steps if cmp(t))

    dPV = temp2 - temp1
    dCO = hd2 - hd1

    return tend - tstart, dPV / dCO


def main():
    pv = sim.current_temp
    sec = D('1')
    try:
        while True:
            hd = pid.step_output(pv, sec)
            pv = sim.step_heat(hd, sec)[1]
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    # plot_fourier()
    sim = TempSim(25, 20, 0)
    pid = PIDController(37, 40, 6)
    pv = sim.current_temp
    sec = D('1')

    main()
