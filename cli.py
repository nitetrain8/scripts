"""

Created by: Nathan Starkweather
Created on: 03/19/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


from decimal import Decimal as D
from time import perf_counter as _timer


def y_of_t(tf, y0=D(25), incr=D(1), Kp=D('2.47938'), A=D('5'), tp=D(22000)):
    tf = D(tf)
    y0 = D(y0)
    incr = D(incr)
    Kp = D(Kp)
    A = D(A)
    tp = D(tp)
    t = D(0)
    one = D(1)

    while t < tf:
        e_exp = -t / tp
        parg = one - e_exp.exp()
        yt = A*Kp*parg
        yt += y0
        yield t, yt
        t += incr


def test1(tf):
    return [(int(t), str(v)) for t, v in y_of_t(tf)]



def iter1(sim, loops):
    timer = _timer
    t1 = timer()
    sim.iterate(loops)
    t2 = timer()
    return D(t2) - D(t1)


def iter2(sim, loops):
    timer = _timer
    t1 = timer()
    sim.iterate2(loops)
    t2 = timer()
    return D(t2) - D(t1)


def run_itertest(oldsim, newsim, loops=200000):
    try:
        while True:
            print("Starmap: %.4f" % iter1(oldsim, loops), "ListComp: %.4f" % iter2(newsim, loops))
    except KeyboardInterrupt:
        pass


def run_pidtest(pid, sim, n=1000):
    """
    @param pid: scripts.run.temp_sim.PIDController
    @type pid: scripts.run.temp_sim.PIDController
    @param sim: scripts.run.temp_sim.TempSim
    @type sim: scripts.run.temp_sim.TempSim
    @param n:
    @type n: int
    """
    pv = sim.current_temp
    try:
        while True:
            for _ in range(n):
                hd = pid.step_output(pv)
                pv = sim.step_heat(hd)[1]
            print("Temp: %.2f" % sim.current_temp, "Output: %.2f" % pid.current_output)
            # print("HD: %.2f" % hd, "PV: %.2f" % pv)
    except KeyboardInterrupt:
        return pid, sim


def plotpid(n=15000):
    import sys
    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import TempSim, PIDController

    sim = TempSim(D('28.183533'), 19, 0)
    pid = PIDController(37, 40, 6)

    pv = sim.current_temp
    steps = [('0', '0', '0', '0', '0') for _ in range(11)]
    for _ in range(n):
        hd = pid.step_output(pv)
        t, pv = sim.step_heat(hd)
        # noinspection PyTypeChecker
        steps.append((t, pv, pid._last_error, pid.accumulated_error, hd))

    from officelib.xllib.xlcom import xlBook2
    xl, wb = xlBook2('PID.xlsx')
    ws = wb.Worksheets(2)
    cells = ws.Cells

    cells.Range(cells(2, 14), cells(len(steps) + 1, len(steps[0]) + 13)).Value = \
        [[str(x) for x in data] for data in steps]


def plotsim(n=7200):
    try:
        import sys
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import TempSim
    sim = TempSim(D('37.04'), 19, 0)
    steps = sim.iterate(n)
    from officelib.xllib.xlcom import xlBook2
    xl, wb = xlBook2('PID.xlsx')

    ws = wb.Worksheets(2)
    cells = ws.Cells
    cells.Range(cells(2, 14), cells(len(steps) + 1, 15)).Value = [(str(t), str(v)) for t, v in steps]

