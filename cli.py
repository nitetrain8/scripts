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


def nextlinething():
    lines = ["foo", '', '', "bar", '', "baz", 0, "bob"]
    liter = iter(lines)
    line = ''
    lineno = 0

    def next_line():
        nonlocal line, lineno, liter
        line = next(liter, None)
        while not line:
            line = next(liter, None)
            lineno += 1
        return line is not None

    while next_line():
        print(line, lineno)


def reload():
    import sys
    try:
        del sys.modules['scripts.cli']
    except:
        pass
    g = sys.modules['__main__'].__dict__
    exec("from scripts.cli import*", g, g)



# globalconst- iter, range, next, StopIteration, Decimal (D), print


def trycontext(n=100000):

    while True:
        from time import perf_counter as timer
        i = iter(range(n))
        t1 = timer()
        while True:
            try:
                next(i)
            except StopIteration:
                break
        t2 = timer()
        # print("small try", t2 - t1)
        i = iter(range(n))
        t3 = timer()
        try:
            while True:
                next(i)
        except StopIteration:
            pass
        t4 = timer()

        tsmall = D(t2) - D(t1)
        tbig = D(t4) - D(t3)

        fastest = "Small Try" if tsmall < tbig else "Big Try"

        print("small try %.8f" % tsmall, "big try %.8f" % tbig, "fastest:", fastest, "%%%.1f" % ((tsmall-tbig)/tsmall * 100))


import ast
import opcode
import dis

class MyVisitor(ast.NodeVisitor):
    def generic_visit(self, node):
        print(node)
        for attr in dir(node):
            try:
                print(getattr(node, attr))
            except Exception as e:
                print("Getattr exception", e)


def hackee(foo):
    length = len(foo)
    print(length)
    bar = next(foo)
    foo.baz()
    return bar


def hack(f=hackee):
    """
    @type f: types.FunctionType
    """
    print(f)
    #: @type: types.CodeType
    code = f.__code__
    for attr in dir(code):
        if not attr.startswith('__'):
            print(attr, getattr(code, attr))

    LOAD_FAST = dis.opmap['LOAD_FAST']
    i = 0
    # for x in code.co_code:
    #     if x == LOAD_FAST:
    #         print(code)
    #         name = code.co_consts[code.co_code[i + 1]]
    #         print(x, dis.opname[x], name)
    #     i += 1


def c1(_len=len):
    a = [1, 2, 3]
    b = (1, 2, 3)
    _len(b)
    return a



a = b = c = None


def disassemble(co, lasti=-1):
    """Disassemble a code object."""
    code = co.co_code
    labels = dis.findlabels(code)
    linestarts = dict(dis.findlinestarts(co))
    n = len(code)
    i = 0
    extended_arg = 0
    free = None
    while i < n:
        print("DEBUG I IS", i, end='')
        op = code[i]
        if i in linestarts:
            if i > 0:
                print()
            print("%3d" % linestarts[i], end=' ')
        else:
            print('   ', end=' ')

        if i == lasti: print('-->', end=' ')
        else: print('   ', end=' ')
        if i in labels: print('>>', end=' ')
        else: print('  ', end=' ')
        print(repr(i).rjust(4), end=' ')
        print(opcode.opname[op].ljust(20), end=' ')
        i = i+1
        if op >= opcode.HAVE_ARGUMENT:
            oparg = code[i] + code[i+1]*256 + extended_arg
            extended_arg = 0
            i = i+2
            if op == opcode.EXTENDED_ARG:
                extended_arg = oparg*65536
            print(repr(oparg).rjust(5), end=' ')
            if op in opcode.hasconst:
                print('(' + repr(co.co_consts[oparg]) + ')', end=' ')
            elif op in opcode.hasname:
                print('(' + co.co_names[oparg] + ')', end=' ')
            elif op in opcode.hasjrel:
                print('(to ' + repr(i + oparg) + ')', end=' ')
            elif op in opcode.haslocal:
                print('(' + co.co_varnames[oparg] + ')', end=' ')
            elif op in opcode.hascompare:
                print('(' + opcode.cmp_op[oparg] + ')', end=' ')
            elif op in opcode.hasfree:
                if free is None:
                    free = co.co_cellvars + co.co_freevars
                print('(' + free[oparg] + ')', end=' ')
            elif op in opcode.hasnargs:
                print('(%d positional, %d keyword pair)'
                      % (code[i-2], code[i-1]), end=' ')
        print()























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


def fudge(i, pv_next, pv_prev, t_next, t_prev):
    return (D(i - t_prev) / D(t_next - t_prev)) * D(pv_next - pv_prev) + pv_prev


def supermath2():
    import sys
    # try:
    #     del sys.modules['scripts.run.temp_sim']
    # except KeyError:
    #     pass
    from officelib.xllib.xlcom import xlBook2
    xl, wb = xlBook2("PID.xlsx")

    ws = wb.Worksheets(2)
    #: @type: officelib.xllib.typehint.th0x1x6.Range.Range
    cells = ws.Cells
    cell_range = cells.Range
    startcell = cells(2, 11)
    endcell = cells(startcell.End(xlDown).Row, 12)
    refdata = cell_range(startcell, endcell).Value2

    times, pvs = zip(*refdata)
    times = tuple(map(int, times))
    pvs = tuple(map(D, pvs))

    t_start = times[0]
    t_end = times[-1]
    pv_start = pvs[0]

    testdata = [pv_start for _ in range(t_start)]
    testdata.extend(0 for _ in range(t_end - t_start + 1))

    data = zip(times, pvs)
    t_prev, pv_prev = next(data)
    i = t_prev
    testdata[i] = pv_prev

    for t_next, pv_next in data:
        i = t_prev
        testdata[i] = pv_prev

        while i < t_next:
            i += 1
            testdata[i] = fudge(i, pv_next, pv_prev, t_next, t_prev)

        t_prev = t_next
        pv_prev = pv_next

    return testdata


def superplot2():
    testdata = supermath2()
    xldata = tuple((t, pv) for t, pv in enumerate(map(str, testdata)))
    ltd = len(testdata)

    from pickle import load
    with open("C:\\\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\scripts\\run\\data\\ref_real.pickle", 'rb') as f:
        cached = load(f)

    print(all(a == b for a, b in zip(testdata, cached)))

    # from officelib.xllib.xlcom import xlBook2
    # xl, wb = xlBook2("PID.xlsx")
    # ws = wb.Worksheets(3)
    # cells = ws.Cells

    firstcol = 1
    # print("Function disabled to avoid overriding data")
    # cells.Range(cells(2, firstcol), cells(ltd + 1, firstcol + 1)).Value = testdata

from itertools import repeat


def plot(x, y, *args):
    from matplotlib import pyplot as plt
    plt.scatter(x, y)
    errors = []
    if args:
        for arg in args:
            try:
                plt.plot(arg)
            except Exception as e:
                errors.append(e)
    if errors:
        print("Errors found:")
        print(*errors, sep='\n')

    plt.show()


def manyplot(n=100, temp=37):

    from matplotlib import pyplot as plt
    from scripts.run.temp_sim import HeatSink

    xdata = tuple(range(n))
    ydata = tuple(temp for _ in range(n))

    plt.scatter(xdata, ydata, label='ref')
    step = HeatSink.step

    for rate100 in range(2, 10, 1):

        rate = rate100 / 100
        sink = HeatSink(rate)

        ydata = [step(sink, temp) for _ in range(n)]
        plt.plot(ydata, label='%d' % rate100)
        print(sink.current)

    plt.show()


def process(sim, pid, n=9532):
    """
    @param sim:
    @type sim: scripts.run.temp_sim.TempSim
    @param pid:
    @type pid: scripts.run.temp_sim.PIDController
    @param n:
    @type n:
    @return:
    @rtype:
    """
    pv = sim.current_temp
    pid.auto_mode(pv)

    simstep = sim.step_heat
    pidstep = pid.step_output

    times = [None] * n
    pvs = [None] * n
    hds = [None] * n

    for i in range(n):
        hd = pidstep(pv)
        t, pv = simstep(hd)
        times[i] = t
        pvs[i] = pv
        hds[i] = hd

    return times, pvs


ref_data = None


def supermath3(delay=0, leak_max=1):
    import sys
    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import TempSim, PIDController

    from pickle import load
    reffile = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\scripts\\run\\data\\ref_real.pickle"
    global ref_data
    if ref_data is None:
        with open(reffile, 'rb') as f:
            ref_data = load(f)

    pid_kwargs = {
        'pgain' : 40,
        'itime' : .5,
        }

    sim_kwargs = {
        'start_temp' : (D('28.18353')),
        'env_temp' : 19,
        'cool_constant' : TempSim.cooling_constant,
        'heat_constant' : TempSim.heating_constant,
        'delay' : delay,
        'leak_max' : leak_max
    }

    sim = TempSim(**sim_kwargs)
    pid = PIDController(37, **pid_kwargs)

    times, pvs = process(sim, pid)
    return times, pvs
    # xldata = tuple(zip(map(str, times), map(str, pvs)))
    # plotxl(19, xldata)
    #
    # sub = D.__sub__
    #
    # totaldiff = sum(map(abs, map(sub, ref_data, pvs)))
    # print("Delay:", sim_kwargs['delay'], end=' ')
    # print("Totaldiff:", totaldiff, end=' ')
    # print("Ave_diff:", totaldiff / len(ref_data))
    #
    # return totaldiff


    # plot(times, pvs, ref_data)

def plotxl(firstcol, data):
    from officelib.xllib.xlcom import xlBook2
    xl, wb = xlBook2("PID.xlsx")
    ws = wb.Worksheets(2)
    cells = ws.Cells

    startcell = cells(2, firstcol)
    endcell = cells(len(data) + 1, firstcol + 1)

    cells.Range(startcell, endcell).Value = data


def profile(cmd):
    from cProfile import run
    from pstats import Stats

    from tempfile import NamedTemporaryFile
    tmpfile = NamedTemporaryFile().name

    from os.path import dirname
    statsfile = dirname(__file__) + "\\stats.txt"

    run(cmd, tmpfile)
    with open(statsfile, 'w') as f:
        s = Stats(tmpfile, stream=f)

        s.sort_stats('time')
        s.print_stats(0.2)

    from os import startfile, remove
    startfile(statsfile)
    remove(statsfile)


def manysuper3():
    d = 0
    last = 99999999999
    totaldiff = 0
    from officelib.xllib.xlcom import xlBook2
    xl, wb = xlBook2("PID.xlsx")
    cell = wb.Worksheets(1).Cells.Range("C8")
    try:
        while True:
            totaldiff = supermath3(d)
            cell.Value = d
            d += 10
    except KeyboardInterrupt:
        pass

    return d, totaldiff


def test_leak():
    data = []

    times, pvs = supermath3(leak_max=0)
    data.append(times)
    data.append(pvs)
    for r in range(1, 11):
        rate = D(r) / 10
        _, pvs = supermath3(leak_max=rate)
        data.append(pvs)

    plot(*data)
