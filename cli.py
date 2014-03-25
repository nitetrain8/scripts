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
    pid = PIDController(37, 40, D('0.55'))
    # pid = PIDController(37, 40, 0.5)
    pid.auto_mode(sim.current_temp)

    pv = sim.current_temp
    #: @type: list[tuple[D]]
    steps = [('0', '0', '0', '0', '0') for _ in range(11)]
    for _ in range(n):
        hd = pid.step_output(pv)
        t, pv = sim.step_heat(hd)
        steps.append((t, pv, pid.last_error, pid.accumulated_error, hd))

    from officelib.xllib.xlcom import xlBook2
    xl, wb = xlBook2('PID.xlsx')
    ws = wb.Worksheets(2)
    cells = ws.Cells

    firstcol = 19

    cells.Range(cells(1, firstcol), cells(1, firstcol + 4)).Value = ("Time", "Temp", "LastErr", "AccumErr", "HeatDuty%")
    cells.Range(cells(2, firstcol), cells(len(steps) + 1, len(steps[0]) + firstcol - 1)).Value = \
        [tuple(map(str, data)) for data in steps]


def plotpid2(n=15000):
    import sys

    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import TempSim, PIDController

    sim = TempSim(D('28.183533'), 19, 0)
    pid = PIDController(37, 40, D('0.55'))
    # pid = PIDController(37, 40, 0.5)
    pid.auto_mode(sim.current_temp)

    pv = sim.current_temp
    #: @type: list[tuple[D]]
    steps = [('0', '0', '0', '0', '0') for _ in range(11)]
    for _ in range(n):
        hd = pid.step_output(pv)
        t, pv = sim.step_heat(hd)
        steps.append((t, pv, pid.last_error, pid.accumulated_error, hd))

    from officelib.xllib.xlcom import xlBook2

    xl, wb = xlBook2('PID.xlsx')
    ws = wb.Worksheets(2)
    cells = ws.Cells

    firstcol = 30

    cells.Range(cells(1, firstcol), cells(1, firstcol + 4)).Value = (
        "Time", "Temp", "LastErr", "AccumErr", "HeatDuty%")
    cells.Range(cells(2, firstcol), cells(len(steps) + 1, len(steps[0]) + firstcol - 1)).Value = \
        [tuple(map(str, data)) for data in steps]


def plotpid3(n=7202 - 11, p=40, i=D('6'), d=0):
    import sys

    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import TempSim, PIDController

    sim = TempSim(D('28.183533'), 19, 0)
    pid = PIDController(37, p, i, d)
    # pid = PIDController(37, 40, 0.5)
    pid.auto_mode(sim.current_temp)

    pv = sim.current_temp
    #: @type: list[tuple[D]]
    steps = [('0', '0', '0', '0', '0') for _ in range(11)]
    for _ in range(n):
        hd = pid.step_output(pv)
        t, pv = sim.step_heat(hd)
        steps.append((t, pv, pid.last_error, pid.accumulated_error, hd))

    from officelib.xllib.xlcom import xlBook2

    xl, wb = xlBook2('PID.xlsx')
    ws = wb.Worksheets(2)
    cells = ws.Cells

    firstcol = 44

    cells.Range(cells(1, firstcol), cells(1, firstcol + 4)).Value = (
        "Time", "Tempp%di%.1f" % (p, i), "LastErr", "AccumErr", "HeatDuty%")
    cells.Range(cells(2, firstcol), cells(len(steps) + 1, len(steps[0]) + firstcol - 1)).Value = \
        [tuple(map(str, data)) for data in steps]

    print(sim)
    print(pid)

def check():
    import sys
    n = 15000
    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import TempSim, PIDController

    sim = TempSim(D('28.183533'), 19, 0)
    pid = PIDController(37, 40, D('0.55'))

    pid.auto_mode(sim.current_temp)

    pv = sim.current_temp
    #: @type: list[tuple[D]]
    steps1 = []
    ap = steps1.append
    for _ in range(n):
        hd = pid.step_output(pv)
        t, pv = sim.step_heat(hd)
        ap((t, pv))

    sim = TempSim(D('28.183533'), 19, 0)

    def auto_mode(self, pv):
        e_t = self.set_point - pv
        self.accumulated_error = - e_t * self.pgain * self.itime

    PIDController.auto_mode = auto_mode

    pid = PIDController(37, 40, D('0.55'))

    pid.auto_mode(sim.current_temp)

    pv = sim.current_temp
    #: @type: list[tuple[D]]
    steps2 = []
    ap = steps2.append
    for _ in range(n):
        hd = pid.step_output(pv)
        t, pv = sim.step_heat(hd)
        ap((t, pv))

    from decimal import Context
    ctxt = Context(prec=3)

    def eq(one, two, ctxt=ctxt, compare=D.compare):
        return not (compare(one[0], two[0], ctxt) and compare(one[1], two[1], ctxt))

    diff = [(i, one, two) for i, (one, two) in enumerate(zip(steps1, steps2)) if not eq(one, two)]
    return diff


def plotsim(n=7200, c=D('-0.00004679011328')):
    try:
        import sys
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import TempSim
    sim = TempSim(D('37.115'), 19, 0, c)
    steps = sim.iterate(n)
    from officelib.xllib.xlcom import xlBook2
    xl, wb = xlBook2('PID.xlsx')

    ws = wb.Worksheets(2)
    cells = ws.Cells

    firstcol = 19

    cells.Range(cells(2, firstcol), cells(len(steps) + 1, firstcol + 1)).Value = [(str(t), str(v)) for t, v in steps]


from officelib.xllib.xladdress import cellRangeStr
from officelib.const import xlDown


def get_regression(cells, startrow, startcol):

    end_row = cells(startrow, startcol).End(xlDown).Row
    xrange = cellRangeStr((startrow, startcol), (end_row, startcol))
    yrange = cellRangeStr((startrow, startcol + 1), (end_row, startcol + 1))
    linest_formula = "=linest(%s, %s)" % (yrange, xrange)
    cells.Range(cells(startrow, startcol + 2), cells(startrow, startcol + 3)).FormulaArray = linest_formula
    m = cells(startrow, startcol + 2).Value2
    b = cells(startrow, startcol + 3).Value2
    m = D(m)
    b = D(b)
    return m, b


def supermath():
    from officelib.xllib.xlcom import xlBook2

    xl, wb = xlBook2("PID.xlsx")
    ws = wb.Worksheets(2)
    cells = ws.Cells
    xl.Visible = False
    n = 5400

    # use excel to do regression work for us.
    ref_m, ref_b = get_regression(cells, 2, 20)
    refdata = [ref_m * i + ref_b for i in range(1, n + 1)]  # start at 1

    print("ref m: %.6f" % ref_m, "ref b: %.6f" % ref_b)

    c = D('-0.0000615198895')
    start_temp = D('37.04')
    best_diff = 9999999999
    try:
        while True:

            steps = run_decay_test(n, start_temp, c)
            strsteps = [(str(t), str(v)) for t, v in steps]
            ws = wb.Worksheets(3)
            cells = ws.Cells
            cell_range = cells.Range

            ls = len(steps)
            cell_range(cells(1, 1), cells(ls, 2)).Value = strsteps
            m, b = get_regression(cells, 1, 1)

            print("c: %s" % c, "m: %.8f" % m, "b:  %.8f" % b)

            pvs = [tpl[1] for tpl in steps]

            diffs = map(D.__sub__, refdata, pvs)
            totaldiff = sum(diffs)

            if totaldiff < best_diff:
                best_diff = totaldiff
            else:
                start_temp += totaldiff / len(pvs)

            print("totaldiff: %.8f" % totaldiff)

            c = (ref_m / m) * c
            # start_temp += ref_b - b

    except:
        return c, m, b, start_temp
    finally:
        xl.Visible = True

    return c, m, b, start_temp


from scripts.run.temp_sim import TempSim


def run_decay_test(n=5400, start_temp=D('37.04'), c=TempSim.cooling_constant):
    """
    @return:
    @rtype:
    """
    sim = TempSim(start_temp, 19, 0, D(c))
    steps = sim.iterate(n)

    return steps


def manyboth():
    import sys
    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import TempSim
    from random import uniform
    Decimal = D
    rnd_2_const = Decimal('-1e-5')
    repr_quant = Decimal("1.00000000000")
    tcs = []
    kps = []
    cs = []

    hd1 = Decimal(6.8)
    hd2 = Decimal(0)

    try:
        while True:

            rnd = uniform(4, 7.5)
            cconst = Decimal(rnd) * rnd_2_const
            sim = TempSim(D('37.114'), 19, hd1, cconst)

            sim.quietiter(250000)
            temp1 = sim.current_temp
            tstart = sim.seconds
            sim.heat_duty = hd2

            bump_steps = sim.iterate(250000)
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

            tc = tend - tstart
            kp = dPV / dCO
            tcs.append(tc)
            kps.append(kp)
            cs.append(sim.cooling_constant)

            print("Const:", sim.cooling_constant.quantize(repr_quant), "Ti:", int(tc), "Kp:", kp.quantize(repr_quant))
    except KeyboardInterrupt:
        return list(zip(cs, tcs, kps))
        # pass


def howlong(n=0, ref_n=1000000, st=D("37.115")):
    import sys
    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import est_both

    print("Generating ref data...")
    ref_ti, _ = est_both(6.8, 0, st, ref_n)
    ti = 0

    print("Ref info: Ti: %d with %d iterations" % (ref_ti, ref_n))

    while ti < ref_ti:
        n += 50000
        print("Testing %d iterations" % n)
        ti, _ = est_both(6.8, 0, st, n)
        print("Result: %d" % ti)

    print("Minimum estimated iterations for accuracy: %d" % n)


def supermath2():
    import sys
    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from officelib.xllib.xlcom import xlBook2
    xl, wb = xlBook2("PID.xlsx")

    ws = wb.Worksheets(2)
    #: @type: officelib.xllib.typehint.th0x1x6.Range.Range
    cells = ws.Cells
    cell_range = cells.Range
    startcell = cells(2, 11)
    endcell = cells(startcell.End(xlDown).Row, 12)
    refdata = cell_range(startcell, endcell).Value2

    end = int(refdata[-1][0])
    testdata = [None] * end
    i = 0
    rd = iter(refdata)
    t_last, pv_last = next(rd)
    t_next, pv_next = next(rd)

    t_last = int(t_last)
    pv_last = float(pv_last)
    t_next = int(t_next)
    pv_next = float(pv_next)

    testdata[0] = t_last

    while i < end:
        t_diff = t_next - t_last
        pv_diff = pv_next - pv_last
        while i < t_next - 1:
            try:
                testdata[i] = ((i - t_last) / t_diff) * pv_diff + pv_last
            except IndexError:
                print(i, len(testdata), len(refdata), t_next)
                raise
            i += 1
        if i >= end:
            break
        i += 1
        testdata[i] = t_next
        t_last, pv_last = t_next, pv_next
        t_next, pv_next = next(rd)

    return testdata




