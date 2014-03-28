"""

Created by: Nathan Starkweather
Created on: 03/19/2014
Created in: PyCharm Community Edition


"""
from officelib.const.const import xlByRows

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
        yt = A * Kp * parg
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
    m = b = None
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

        # noinspection PyStringFormat
        print("small try %.8f" % tsmall, "big try %.8f" % tbig, "fastest:", fastest,
              "%%%.1f" % ((tsmall - tbig) / tsmall * 100))


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


# noinspection PyUnusedLocal
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

        if i == lasti:
            print('-->', end=' ')
        else:
            print('   ', end=' ')
        if i in labels:
            print('>>', end=' ')
        else:
            print('  ', end=' ')
        print(repr(i).rjust(4), end=' ')
        print(opcode.opname[op].ljust(20), end=' ')
        i += 1
        if op >= opcode.HAVE_ARGUMENT:
            oparg = code[i] + code[i + 1] * 256 + extended_arg
            extended_arg = 0
            i += 2
            if op == opcode.EXTENDED_ARG:
                extended_arg = oparg * 65536
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
                      % (code[i - 2], code[i - 1]), end=' ')
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


def fudge(i, pv_next, pv_prev, t_next, t_prev, D=D):
    return (D(i - t_prev) / D(t_next - t_prev)) * D(pv_next - pv_prev) + pv_prev


def smooth_data(x_data, y_data):

    # from officelib.xllib.xlcom import xlBook2
    #
    # xl, wb = xlBook2("PID.xlsx")
    #
    # ws = wb.Worksheets(2)
    # #: @type: officelib.xllib.typehint.th0x1x6.Range.Range
    # cells = ws.Cells
    # cell_range = cells.Range
    # startcell = cells(2, 11)
    # endcell = cells(startcell.End(xlDown).Row, 12)
    # refdata = cell_range(startcell, endcell).Value2

    times = tuple(map(round, x_data))
    pvs = tuple(map(D, y_data))

    t_start = times[0]
    t_end = times[-1]
    pv_start = pvs[0]

    new_ys = [pv_start for _ in range(t_start or 1)]
    new_ys.extend(range(t_end - len(new_ys) + 1))

    data = zip(times, pvs)
    t_prev, pv_prev = next(data)
    i = t_prev
    new_ys[i] = pv_prev
    _fudge = fudge
    dec = D
    import pdb
    for t_next, pv_next in data:
        # new_ys[i] = pv_prev
        while i < t_next:
            i += 1
            # if i == 5:
            #     pdb.set_trace()
            result = _fudge(i, pv_next, pv_prev, t_next, t_prev, dec)
            new_ys[i] = result

        t_prev = t_next
        pv_prev = pv_next
    new_ys[-1] = pvs[-1]

    x_data = tuple(range(len(new_ys)))

    return x_data, new_ys


def plot(x, y, y_data=(), names=()):
    from matplotlib import pyplot as plt
    from itertools import count, cycle
    from random import randrange, random

    cnt = count(1)
    markers = (',', '.', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_')
    start = randrange(0, len(markers))
    next_marker = cycle(markers).__next__

    for _ in range(start):
        next_marker()

    def next_name(n_iter=iter(names)):
        # can't use next(iter, fallback)
        # with count, need to make sure
        # next(count) is evaluated lazily
        nxt = next(n_iter, None)
        if nxt is None:
            return "Series " + str(next(cnt))
        return nxt

    def rand_color():
        return random(), random(), random()

    plts = [plt.scatter(x, y, 20, color=rand_color(), marker=next_marker())]
    good_names = [next_name()]

    errors = []
    if y_data:
        for y in y_data:
            try:
                plts.append(plt.scatter(x, y, 20, color=rand_color(), marker=next_marker()))
            except Exception as e:
                errors.append(e)
                next_name()  # dump unused name
            else:
                good_names.append(next_name())
    if errors:
        print("Errors found:")
        print(*errors, sep='\n')

    if good_names:
        plt.legend(plts, names,
                   scatterpoints=1)
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


_ref_data = None
_ref_map = None


def get_ref_data():
    """
    @return:
    @rtype: list[xlData]
    """
    global _ref_data, _ref_map
    if _ref_data is None:
        _ref_data = sorted(cli_load("PID.xlsx_ws_3.pickle"), key=lambda x: D(x.itime))
    return list(map(xlData.copy, _ref_data))


def get_ref_map():
    """
    @return:
    @rtype: dict[str, xlData]
    """
    global _ref_map
    if _ref_map is None:
        ref_data = get_ref_data()
        _ref_map = {d.itime: d for d in map(xlData.copy, ref_data)}
    return {d.itime: d for d in map(xlData.copy, _ref_map.values())}


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


# noinspection PyUnusedLocal
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


def fix_typehint():
    th_path = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\typehint.py"
    from io import StringIO, SEEK_END
    # buf = StringIO()
    with open(th_path, 'r') as f:
        buf = StringIO(f.read())

    buf.seek(0, SEEK_END)

    write = buf.write

    write("\n\n")

    th_dir = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\officelib\\xllib\\typehint"
    from os import listdir
    from os.path import splitext
    from importlib import import_module

    import_str = "officelib.xllib.typehint.%s.%s"

    for f in listdir(th_dir):
        path = '\\'.join((th_dir, f))
        try:
            for module in listdir(path):

                module = splitext(module)[0]
                mod_str = import_str % (f, module)
                if "__" in mod_str:
                    continue
                m = import_module(mod_str)
                cls_list = [attr for attr in dir(m) if not "__" in attr and isinstance(getattr(m, attr), type)]
                try:
                    cls_list.remove("DispatchBaseClass")
                except:
                    pass
                attr_str = ', '.join(cls_list)
                if attr_str:

                    write("# noinspection PyUnresolvedReferences\n")
                    write("".join(("from ", mod_str, " import ", attr_str, '\n')))

        except NotADirectoryError:
            continue

    new = buf.getvalue()

    derp = False

    if derp:
        stream = open(th_path, 'w')
    else:
        import sys
        stream = sys.stdout

    print(new, file=stream)

    if derp:
        stream.close()


def get_test_data(name_cell):

    from scripts.tpid.tpidmany import RampTestResult
    # from officelib.xllib.xladdress import cellStr
    cells = name_cell.Parent.Cells
    start_row = name_cell.Row
    start_col = name_cell.Column
    # x_range = cells.Range(cells(start_row + 7, start_col + 1), cells(start_row + 7, start_col + 1).End(xlDown))
    # y_range = cells.Range(cells(start_row + 7, start_col + 3), cells(start_row + 7, start_col + 3).End(xlDown))

    def getval(row, col):
        row += start_row
        col += start_col
        return cells(row, col).Value
    # print("getting data")
    r = RampTestResult(
        getval(1, 2),
        getval(2, 2),
        0,
        None,
        None,
        0,
        0,
        getval(0, 1),
    )

    # x_data = tuple(x[0] for x in x_range.Value)
    # y_data = tuple(y[0] for y in y_range.Value)
    #
    # if type(x_data[0]) is not float:
    #     raise TypeError(type(x_data[0]), cellStr(row, col))
    # if type(y_data[0]) is not float:
    #     raise TypeError(type(y_data[0]), cellStr(row, col))
    # r.x_data = x_data
    # r.y_data = y_data
    return r


# noinspection PyUnresolvedReferences
def xl_2_data():

    from officelib.xllib.xlcom import xlBook2, HiddenXl
    from officelib.xllib.xladdress import cellStr

    fpath = "C:\\users\\public\\documents\\pbsss\\temp pid\\pbs 3 thick sleeve\\compiled.xlsx"
    xl, wb = xlBook2(fpath)

    ws = wb.Worksheets("ProcedureEx")
    #: @type: typehint.Range
    cells = ws.Cells

    found = set()
    # tests = []

    def cell_hash(cell):
        to_hash = (cell.Row, cell.Column)
        print(to_hash)
        return hash(to_hash)

    with HiddenXl(xl):
        match = cells.Find("Name:", cells(1, 1), SearchOrder=xlByRows)
        h = cell_hash(match)
        found.add(h)
        tests = [get_test_data(match)]
        while True:
            match = cells.FindNext(match)
            h = cell_hash(match)
            if h in found:
                break
            else:
                found.add(h)
            test = get_test_data(match)
            tests.append(test)

    return tests


def cli_store(data, name="Cli_data"):
    from pysrc.snippets import safe_pickle
    from os.path import dirname
    save_dir = dirname(__file__) + '\\cli_data\\'
    save_name = save_dir + name + ".pickle"
    safe_pickle(data, save_name)
    return save_name


def cli_load(name):

    from os.path import dirname
    from pickle import load
    save_dir = dirname(__file__) + '\\cli_data\\'
    save_name = save_dir + name
    with open(save_name, 'rb') as f:
        data = load(f)
    return data


class xlData():
    def __init__(self, name, x_data, y_data, pgain='0', itime='0'):
        self.itime = itime
        self.pgain = pgain
        self.name = name
        self.x_data = tuple(map(round, x_data))
        self.y_data = tuple(map(D, y_data))

    @classmethod
    def copy(cls, obj):
        """ This is necessary to allow instances of xlData
        to persist across module reloads at the interactive
        prompt, so that the method
        can be called on existing instances to return a picklable
        copy; otherwise type(inst) == xlData returns false.
        """
        return cls(obj.name, obj.x_data, obj.y_data, obj.pgain, obj.itime)

    def __repr__(self):
        return ' '.join(("<", self.__class__.__qualname__, ">", self.name, str(self.pgain), str(self.itime)))


def get_xl_data():

    from officelib.xllib.xlcom import xlBook2
    from itertools import dropwhile
    import re

    xl, wb = xlBook2('PID.xlsx')
    ws = wb.Worksheets(3)
    cells = ws.Cells

    columns = (5, 9, 13, 17, 21, 25, 29)

    def bad(tpl):
        x, y = tpl
        return x is None or y < 28

    parse_name = re.compile(r"p(\d*)i([\d\.]*)").match

    all_dat = []
    ap = all_dat.append
    row = 2

    for col in columns:
        xldat = cells.Range(cells(row, col), cells(row, col + 1).End(xlDown)).Value
        name = cells(1, col + 1).Value
        data = dropwhile(bad, xldat)
        x, y = tuple(zip(*data))
        x_data, y_data = smooth_data(x, y)
        p, i = parse_name(name).groups()
        ap(xlData(name, x_data, y_data, p, i))

    return all_dat


# noinspection PyUnusedLocal
def supermath3(delay=0, leak_max=0, ref_data=None, i=D('0.5'), ifactor=D(1), plot=True):
    """
    @param delay:
    @type delay: int | Decimal
    @param leak_max:
    @type leak_max: int | Decimal
    @return:
    @rtype:
    """
    import sys

    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import TempSim, PIDController

    if ref_data is None:
        try:
            ref_data = get_ref_map()[str(i)]
            print(ref_data)
            ref_data = ref_data.y_data
        except:
            ref_data = get_ref_data()[0]
            print(ref_data)
            ref_data = ref_data.y_data

    pid_kwargs = {
        'pgain': 40,
        'itime': D(i) * D(ifactor),
        }

    sim_kwargs = {
        'start_temp': (D('28.18353')),
        'env_temp': 19,
        'cool_constant': TempSim.cooling_constant,
        'heat_constant': TempSim.heating_constant,
        'delay': delay,
        'leak_const': leak_max
    }

    sim = TempSim(**sim_kwargs)
    pid = PIDController(37, **pid_kwargs)

    times, pvs = process(sim, pid)
    fix = D('-1').__add__
    if plot:
        times = map(str, map(fix, times))
        xldata = tuple(zip(times, map(str, pvs)))
        plotxl(xldata, 32, 2, "SimDataP%di%.1f" % (pid_kwargs['pgain'], pid_kwargs['itime']))

    totaldiff = sum(map(abs, map(D.__sub__, ref_data, pvs)))
    # print("Delay:", sim_kwargs['delay'], end=' ')
    # print("Totaldiff:", totaldiff, end=' ')
    # print("Ave_diff:", totaldiff / len(ref_data))

    return ref_data

    # plot(times, pvs, ref_data)
    # return times, pvs

from officelib.xllib.xlcom import xlBook2


def plotxl(data, firstcol=1, firstrow=2,
           y_header="SimData", wb_name="PID.xlsx", ws_num=3):

    xl, wb = xlBook2(wb_name)
    ws = wb.Worksheets(ws_num)
    cells = ws.Cells

    startcell = cells(firstrow, firstcol)
    endcell = cells(len(data) + firstrow - 1, firstcol + len(data[0]) - 1)

    if firstrow > 1:
        cells(firstrow - 1, firstcol + 1).Value = y_header
    cells.Range(startcell, endcell).Value = data

    return startcell, endcell


def manysink():

    import sys
    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import HeatSink

    consts = ('1', '2', '5', '10', '20')
    cs = map(D, consts)
    x_data = tuple(range(100))
    from itertools import islice
    y_data = []

    for c in cs:
        y = []
        y_ap = y.append
        sink = HeatSink(c)
        hd = 50

        for _ in islice(x_data, None, 50):
            step = sink.step(hd)
            y_ap(step)

        hd = 0
        for _ in islice(x_data, 50, None):
            step = sink.step(hd)
            y_ap(step)
        print(sum(y), 50 * 50 - sink.current)
        y_data.append(y)

    # plot(x_data, y_data[0], y_data[1:], consts)

# noinspection PyUnresolvedReferences
import sys


# noinspection PyUnusedLocal
def optimal_i(i=D('2.5')):
    #
    # try:
    #     del sys.modules['scripts.run.temp_sim']
    # except KeyError:
    #     pass

    i = D(i)
    ifactor = D('12')
    i_step = D(2)
    i_step_factor = D('0.5')
    i_step_min = D('1')
    ref_map = get_ref_map()
    ref_data = ref_map[str(i)]
    print(ref_data)
    ref_data = ref_data.y_data

    last_diff = supermath3(0, 0, ref_data, i, ifactor, False)
    diff = last_diff - 1
    ifactor += i_step

    _print = print
    _len = len
    false = False

    try:
        while diff != 0:

            print("going up!", end='\n\n')
            while True:
                diff = supermath3(0, 0, ref_data, i, ifactor, plot=false)
                _print("Ifactor:", ifactor, end=' ')
                _print("Totaldiff:", diff, end=' ')
                _print("Ave_diff:", diff / _len(ref_data))

                if diff > last_diff:
                    break
                lastdiff = diff
                ifactor += i_step

            i_step *= i_step_factor
            if i_step < i_step_min:
                i_step = i_step_min
            ifactor -= i_step
            print("going down!", end='\n\n')

            while True:
                diff = supermath3(0, 0, ref_data, i, ifactor, plot=false)
                _print("Ifactor:", ifactor, end=' ')
                _print("Totaldiff:", diff, end=' ')
                _print("Ave_diff:", diff / _len(ref_data))
                if diff > last_diff:
                    break
                last_diff = diff
                ifactor -= i_step

            i_step *= i_step_factor
            if i_step < i_step_min:
                i_step = i_step_min
            ifactor += i_step

    except KeyboardInterrupt:
        pass

    if diff == 0:
        _print("wow!")

    supermath3(0, 0, ref_data, i, ifactor, plot=True)

    return ifactor

