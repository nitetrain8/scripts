"""

Created by: Nathan Starkweather
Created on: 03/28/2014
Created in: PyCharm Community Edition


"""
from os import listdir
from pysrc.optimize import make_constants
from pysrc.snippets import smooth1
from decimal import Decimal as D
from time import perf_counter as _timer
from scripts.run.temp_sim import TempSim

__author__ = 'Nathan Starkweather'


#==================
# USEFUL FUNCTIONS
#==================


_main_name = '__main__'


def reload():
    import sys

    try:
        del sys.modules['scripts.cli']
    except KeyError:
        pass
    g = sys.modules[_main_name].__dict__
    exec("from scripts.cli import *", g, g)


def reload2():
    import sys

    try:
        del sys.modules['scripts.old_cli']
    except KeyError:
        pass
    g = sys.modules[_main_name].__dict__
    exec("reload()", g, g)


_ref_data = None
_ref_map = None


def get_ref_data():
    """
    @return:
    @rtype: list[xlData]
    """
    global _ref_data, _ref_map
    if _ref_data is None:
        key = lambda x: (D(x.pgain), D(x.itime))
        _ref_data = sorted(cli_load("PID.xlsx_ws_3.pickle"), key=key)
        _ref_data.extend(sorted(cli_load("PID.xlsx_ws_4.pickle"), key=key))
    return list(map(xlData.copy, _ref_data))


def get_ref_map():
    """
    @return:
    @rtype: dict[str, xlData]
    """
    global _ref_map
    if _ref_map is None:
        ref_data = get_ref_data()
        _ref_map = {d.name: d for d in map(xlData.copy, ref_data)}
    return {d.name: d for d in map(xlData.copy, _ref_map.values())}


def cli_store(data, name="Cli_data"):
    from pysrc.snippets import safe_pickle
    from os.path import dirname
    save_dir = dirname(__file__) + '\\cli_data\\'
    save_name = save_dir + name
    if not save_name.endswith(".pickle"):
        save_name += ".pickle"
    safe_pickle(data, save_name)
    return save_name


def cli_load(name):

    from os.path import dirname
    from pickle import load
    save_dir = dirname(__file__) + '\\cli_data\\'
    save_name = save_dir + name
    if not save_name.endswith('.pickle'):
        save_name += '.pickle'
    with open(save_name, 'rb') as f:
        data = load(f)
    return data


def plotxl_by_cell(data, cell, y_header="SimData"):
    firstcol = cell.Column
    firstrow = cell.Row

    ws = cell.Parent
    wb = ws.Parent
    wb_name = wb.Name
    ws_name = ws.Name
    return plotxl(data, firstcol, firstrow, y_header, wb_name, ws_name)


def plotxl(data, firstcol=1, firstrow=2,
           y_header="SimData", wb_name="PID.xlsx", ws_id=3):

    from officelib.xllib.xlcom import xlBook2

    xl, wb = xlBook2(wb_name)
    ws = wb.Worksheets(ws_id)
    cells = ws.Cells

    startcell = cells(firstrow, firstcol)
    endcell = cells(len(data) + firstrow - 1, firstcol + len(data[0]) - 1)

    if y_header and firstrow > 1:
        cells(firstrow - 1, firstcol + 1).Value = y_header
    cells.Range(startcell, endcell).Value = data

    return startcell, endcell


def plot(x, y, *y_data, names=()):
    """
    @param x: x data
    @type x: collections.Iterable[int | float | decimal.Decimal]
    @param y: y data
    @type y: collections.Iterable[int | float | decimal.Decimal]
    @param y_data: any more sets of y data for the x data
    @type y_data: collections.Iterable[int | float | decimal.Decimal]
    @param names: names to pass to legend
    @type names: collections.Iterable[str]
    """
    from matplotlib import pyplot as plt
    from itertools import count, cycle
    from random import randrange, random

    markers = (',', '.', 'o', 'v', '^',
               '<', '>', '1', '2', '3',
               '4', '8', 's', 'p', '*',
               'h', 'H', '+', 'x', 'D', 'd')
    next_marker = cycle(markers).__next__

    # start at a random marker
    rnd_marker_start = randrange(0, len(markers))
    for _ in range(rnd_marker_start):
        next_marker()

    # passed in single name
    if isinstance(names, str):
        names = (names,)
    iternames = iter(names)

    legend = plt.gca().legend_
    if legend is not None:
        handles = legend.legendHandles[:]
        labels = [t.get_text() for t in legend.texts]
    else:
        handles = []
        labels = []

    used_names = set(labels)
    used_names.add(None)

    series_num = count(1)

    def next_name():
        nxt = next(iternames, None)
        if nxt is None:
            while nxt in used_names:
                nxt = "Series %d" % next(series_num)
        elif nxt in used_names:
            i = 0
            new = nxt + str(i)
            while new in used_names:
                i += 1
                new = nxt + str(i)
            nxt = new
        used_names.add(nxt)
        return nxt

    def rand_color():
        return random(), random(), random()

    new_plots = [plt.scatter(x, y, 20, color=rand_color(), marker=next_marker())]
    good_names = [next_name()]

    errors = []
    for y in y_data:
        name = next_name()
        try:
            next_plt = plt.scatter(x, y, 20, color=rand_color(), marker=next_marker())
        except Exception as e:
            errors.append(e)
        else:
            good_names.append(name)
            new_plots.append(next_plt)

    if errors:
        print("Errors found:")
        print(*errors, sep='\n')

    handles.extend(new_plots)
    labels.extend(good_names)

    plt.legend(handles, labels, scatterpoints=1)
    plt.show()


class xlData():
    def __init__(self, name, x_data=(), y_data=(), pgain='0', itime='0'):
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
        copy; otherwise type(obj) == xlData returns false.
        """
        self = cls(obj.name, pgain=obj.pgain, itime=obj.itime)
        self.x_data = tuple(obj.x_data)
        self.y_data = tuple(obj.y_data)
        return self

    def __repr__(self):
        return ' '.join(("<%s>" % type(self).__qualname__, self.name, str(self.pgain), str(self.itime)))

    @classmethod
    def fixlist(cls, list):
        """
        @type list: list[xlData]
        """
        newlist = []
        ap = newlist.append
        for obj in list:
            newobj = cls.copy(obj)
            ap(newobj)
        return newlist


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

    from os import startfile

    startfile(statsfile)
    # remove(statsfile)


def process(sim, pid, n=9532, step_size=1, off_to_auto=True):
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
    if off_to_auto:
        pid.off_to_auto(pv)
    else:
        pid.man_to_auto(sim.heat_duty, pv)

    sim_step = sim.step_heat
    pid_step = pid.step_output

    times = []; times_ap = times.append
    pvs = []; pvs_ap = pvs.append
    hds = []; hds_ap = hds.append

    step_size = D(step_size)

    for _ in range(n):
        hd = pid_step(pv, step_size)
        t, pv = sim_step(hd, step_size)
        times_ap(t)
        pvs_ap(pv)
        hds_ap(hd)

    # print(sim)
    # print(pid)

    return times, pvs, hds


#==================
# END USEFUL FUNCTIONS
#==================


def get_regression(cells, startrow, startcol):

    from officelib.xllib.xladdress import cellRangeStr
    from officelib.const import xlDown

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


# noinspection PyUnusedLocal
def manysuper3():
    d = 0
    last = 99999999999
    totaldiff = 0
    from officelib.xllib.xlcom import xlBook2
    from scripts.cli import supermath3

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
    from scripts.cli import supermath3
    times, pvs = supermath3(leak_constant=0)
    data.append(times)
    data.append(pvs)
    for r in range(1, 11):
        rate = D(r) / 10
        _, pvs = supermath3(leak_constant=rate)
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


# noinspection PyUnresolvedReferences
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
            cs.append(sim.cool_rate)

            print("Const:", sim.cool_rate.quantize(repr_quant), "Ti:", int(tc), "Kp:", kp.quantize(repr_quant))
    except KeyboardInterrupt:
        return list(zip(cs, tcs, kps))
        # pass


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


def run_decay_test(n=5400, start_temp=D('37.04'), c=TempSim.DEFAULT_COOL_CONSTANT):
    """
    @return:
    @rtype:
    """
    sim = TempSim(start_temp, 19, 0, D(c))
    steps = sim.iterate(n)

    return steps


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


def plotpid(i=33, ret=False):
    import sys

    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass
    from scripts.run.temp_sim import TempSim, PIDController

    n = 9532
    sim = TempSim(D('28.183533'), 19, 0)
    pid = PIDController(37, 40, D(i))
    # pid = PIDController(37, 40, 0.5)
    pid.off_to_auto(sim.current_temp)

    pv = sim.current_temp
    #: @type: list[tuple[D]]
    steps = []
    append = steps.append
    step_output = pid.step_output
    step_heat = sim.step_heat
    _str = str
    for _ in range(n):
        hd = step_output(pv)
        t, pv = step_heat(hd)
        append((_str(t), _str(pv), _str(pid.last_error), _str(pid.accumulated_error), _str(hd)))

    # from officelib.xllib.xlcom import xlBook2
    # xl, wb = xlBook2('PID.xlsx')
    # ws = wb.Worksheets(2)
    # cells = ws.Cells
    #
    # # xldata = [tuple(map(str, data)) for data in steps]

    firstcol = 19
    firstrow = 13

    plotxl(steps, firstcol, firstrow, '', 'PID.xlsx', 2)

    if ret:
        return steps
    # cells.Range(cells(1, firstcol), cells(1, firstcol + 4)).Value = ("Time", "Temp", "LastErr", "AccumErr", "HeatDuty%")
    # cells.Range(cells(2, firstcol), cells(len(steps) + 1, len(steps[0]) + firstcol - 1)).Value = [tuple(map(str, data)) for data in steps]


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
    pid.off_to_auto(sim.current_temp)

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
    pid.off_to_auto(sim.current_temp)

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

    pid.off_to_auto(sim.current_temp)

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

    PIDController.off_to_auto = auto_mode

    pid = PIDController(37, 40, D('0.55'))

    pid.off_to_auto(sim.current_temp)

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


def get_xl_data():

    from officelib.xllib.xlcom import xlBook2
    from officelib.const import xlDown
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
        x_data, y_data = smooth1(x, y)
        p, i = parse_name(name).groups()
        ap(xlData(name, x_data, y_data, p, i))

    return all_dat


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

    plot(x_data, y_data[0], y_data[1:], consts)


# noinspection PyUnusedLocal
def inplace_speed():
    from time import perf_counter as timer
    _map = map
    n = D(1)
    i = D(1)
    incr = i.__add__

    loops = 100000 * 100

    test_data = tuple(D(1) for _ in range(loops))

    t1 = timer()
    for n in test_data:
        n = incr(n)
    t2 = timer()

    t3 = timer()
    for n in test_data:
        n += i
    t4 = timer()

    t5 = timer()
    for num in _map(incr, test_data):
        a = num
    t6 = timer()

    t7 = timer()
    for num in test_data:
        a = num + i

    t8 = timer()

    print("Incr:", t2 - t1, "normal:", t4 - t3, 'map:', t6 - t5, "comp", t8 - t7)


# noinspection PyGlobalUndefined
def iterspeedtest():

    from itertools import zip_longest, repeat
    bigfile = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\pbslib\\test\\test_batchreport\\test_mock_strptime\\test_input\\real_world_data\\bigfile.csv"

    with open(bigfile, 'r') as f:
        f.readline()
        data = f.read().splitlines()

    # noinspection PyUnusedLocal, PyRedeclaration
    def map_test(mydata=data, _zip_longest=zip_longest, _repeat=repeat):

        mydata2 = _zip_longest(*map(str.split, mydata, _repeat(',')), fillvalue='')
        return mydata2

    # noinspection PyUnusedLocal, PyRedeclaration
    def listcomp_test(data=data, _zip_longest=zip_longest):

        split = str.split
        mydata = _zip_longest(*[split(x, ',') for x in data], fillvalue='')
        return mydata

    # noinspection PyUnusedLocal, PyRedeclaration
    def naive_test(data=data, _zip_longest=zip_longest):

        newdata = []
        append = newdata.append
        split = str.split
        for x in data:
            append(split(x, ','))
        newdata = _zip_longest(*newdata)
        return newdata

    # noinspection PyUnusedLocal, PyRedeclaration
    def map_v_list():
        from timeit import Timer
        from itertools import count
        naive_total = listcomp_total = map_total = 0

        naive_timer = Timer(stmt=naive_test)
        listcomp_timer = Timer(stmt=listcomp_test)
        map_timer = Timer(stmt=map_test)

        # assert map_test() == listcomp_test() == naive_test()

        def key(result):
            return result[1]

        times = 1

        for i in count(1):
            try:

                naive_result = naive_timer.timeit(times)
                naive_total += naive_result
                print("Naive", naive_result)

                listcomp_result = listcomp_timer.timeit(number=times)
                listcomp_total += listcomp_result
                print("listcomp:", listcomp_result)

                map_result = map_timer.timeit(number=times)
                map_total += map_result
                print("map:", map_result)

                results = (
                    ("map", map_total / i),
                    ("listcomp", listcomp_total / i),
                    ("Naive", naive_total / i)
                )

                print('\n', ' '.join("%s: %.3f" % result for result in sorted(results, key=key)), end='\n\n')

            except KeyboardInterrupt:
                break
    import sys
    sys.modules['__main__'].__dict__.update(locals())


bigfile = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\pbslib\\test\\test_batchreport\\test_mock_strptime\\test_input\\real_world_data\\bigfile.csv"
bigfile2 = "C:\\Users\\Administrator\\Documents\\Programming\\python\\pbslib\\test\\test_batchreport\\test_mock_strptime\\test_input\\real_world_data\\bigfile.csv"


def getbigfiledata():

    with open(bigfile2, 'r') as f:
        f.readline()
        data = f.read().splitlines()
    return data


def unpack_test():
    from timeit import Timer
    from itertools import count

    append_total = assigment_total = 0

    data = getbigfiledata()

    def using_append(data=data):
        mydata2 = []
        append = mydata2.append
        split = str.split
        for derp in data:
            append(split(derp, ','))
        return mydata2

    def using_assignment(data=data, len=len):
        mydata2 = [None] * len(data)
        split = str.split
        for i, derp in enumerate(data):
            mydata2[i] = split(derp, ',')

        return mydata2

    append_timer = Timer(stmt=using_append).timeit
    assignment_timer = Timer(stmt=using_assignment).timeit

    def key(result):
        return result[1]

    for i in count(1):
        try:
            append_result = append_timer(1)
            append_total += append_result
            print("append Result:", append_result, end=' ')

            assignment_result = assignment_timer(1)
            assigment_total += assignment_result
            print("assignment Result:", assignment_result)

            results = (
                ("append", append_total / i),
                ("assignment", assigment_total / i)
            )

            print('\n', ' '.join("%s: %.3f" % result for result in sorted(results, key=key)), end='\n\n')

        except KeyboardInterrupt:
            break


from opcode import opmap, HAVE_ARGUMENT


LOAD_CONST = opmap['LOAD_CONST']
STORE_GLOBAL = opmap['STORE_GLOBAL']
EXTENDED_ARG = opmap['EXTENDED_ARG']
LOAD_GLOBAL = opmap['LOAD_GLOBAL']

GREATER_HAVE_ARG = HAVE_ARGUMENT - 1


def dummy_len(_):
    print("Dummy len called")


def dummy_list(_):
    print('Dummy list called')


builtin_dict = {'len': dummy_len,
                'list' : dummy_list}


def testfoo():
    data = (1, 2, 3)
    len(data)
    list(data)
    for d in data:
        print(d, end='')


def iterops(codestr):
    i = 0
    codelen = len(codestr)
    while i < codelen:
        op = codestr[i]
        yield op
        i += 1
        if op > GREATER_HAVE_ARG:
            i += 2


# noinspection PyUnusedLocal
def scancode(f):
    code = f.__code__
    codelen = len(code.co_code)
    newcode = code.co_code
    i = 0

    if any(op == EXTENDED_ARG for op in iterops(newcode)):
        import pdb
        pdb.set_trace()
        # a = 1  #

    return None


def scan_ns(ns=None):

    if ns is None:
        import sys
        for module in sys.modules:
            ns = vars(sys.modules[module])
        for k, v in ns.items():
            if hasattr(v, '__code__'):
                try:
                    scancode(v)
                except AttributeError:
                    pass
    else:
        for k, v in ns.items():
            if hasattr(v, '__code__'):
                try:
                    scancode(v)
                except AttributeError:
                    pass


def derp():

    from os import listdir
    import builtins

    # noinspection PyUnusedLocal
    def dummy_print(*args, **kwargs):
        pass

    path = "C:\\Python33\\Lib"
    files = listdir(path)

    for file in files:
        if file.endswith(".py") and 'setup' not in file and 'antigravity' not in file:
            fpath = '\\'.join((path, file))
            with open(fpath, 'rb') as f:
                src = f.read()

            ns = {'__name__' : '__dummy__'}
            ns.update((k, v) for k, v in vars(builtins).items() if not k.startswith('_'))
            ns['print'] = dummy_print

            try:
                exec(src, ns, ns)
            except Exception as e:
                print("Error scanning:", file, e)
                continue

            print("scanning %s" % file)

            scan_ns(ns)


def testfoo2():
    a = (1, 2, 3, 4, 5)
    for _ in range(100000):
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)
        len(a)


def time_testfoo2():
    from timeit import Timer
    from pysrc.optimize.optimize_constants import _make_constant_globals
    import builtins
    env = vars(builtins).copy()
    env.update(globals())
    before = Timer(testfoo2).timeit

    after = Timer(_make_constant_globals(testfoo2, env)).timeit

    before_total = after_total = 0

    from itertools import count
    n = 3
    for i in count(1):

        bresult = before(n)
        aresult = after(n)

        before_total += bresult
        after_total += aresult

        print()
        print("Before:", bresult, "After:", aresult)
        print("Before Total", before_total / i, "After Total:", after_total / i)
        print()


# noinspection PyUnusedLocal
def optimal_i(i=D('2.5')):
    from scripts.cli import supermath3
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
        while diff:

            print("going up!", end='\n\n')
            while True:
                diff = supermath3(0, 0, ref_data, i, plot=false)
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
                diff = supermath3(0, 0, ref_data, i, plot=false)
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

    supermath3(0, 0, ref_data, i, plot=True)

    return ifactor


# noinspection PyGlobalUndefined
def run_test(op=int.__add__, amt=0.2, itime=2.5):
    # import operator
    from scripts.cli import supermath3
    import sys

    g = sys.modules['__main__'].__dict__
    lastdiff = g['lastdiff']
    i = lasti = g['i']
    ref = g['ref']

    diff = supermath3(95, 0, ref, itime, i, False)

    while True:
        print("Starting again", diff, lastdiff)
        lasti = i
        i = op(i, amt)
        lastdiff = diff
        diff = supermath3(95, 0, ref, itime, i, False)
        if diff >= lastdiff:
            diff = supermath3(95, 0, ref, itime, lasti, True)
            break

    _l = locals().copy()
    _l.pop('lasti')
    _l.pop('amt')
    _l.pop('op')
    _l.pop('itime')
    g.update(_l)
    # print(diff, lastdiff)
    return lasti


# noinspection PyStatementEffect
def foo():
    self


# noinspection PyStatementEffect
class _mc():
    def bar(self):
        self


self = _mc()
self.foo = foo


def method_speed(n=3000000):
    from timeit import Timer
    from pysrc.optimize.optimize_constants import make_constants
    # import builtins

    method = Timer(self.bar).timeit

    self.foo = make_constants(self=self)(foo)
    const = Timer(self.foo).timeit

    method_total = const_total = 0

    from itertools import count
    i = 1
    try:
        for i in count(1):

            aresult = const(n)
            bresult = method(n)

            method_total += bresult
            const_total += aresult

            print()
            print("method:", bresult, "const:", aresult)
            print("method Total", method_total / i, "const Total:", const_total / i)
            print()
    except KeyboardInterrupt:
        return method_total / i, const_total / i


@make_constants(int=int, map=map, tuple=tuple, zip=zip,
                    next=next, enumerate=enumerate, str=str)
def get_m():
    from scripts.cli import delsim
    delsim()
    from scripts.run.temp_sim import TempSim
    from officelib.xllib.xlcom import xlBook2
    # from officelib.xllib.xladdress import cellRangeStr
    from time import sleep
    # from pysrc.snippets import smooth1

    xl, wb = xlBook2('PID.xlsx')
    h = TempSim.DEFAULT_HEAT_CONSTANT

    cells = wb.Worksheets('xtra').Cells

    # refdata = get_paired_cols(cells.Range('E2'))
    # refx, refy = zip(*refdata)
    # refx, refy = smooth1(refx, refy)
    # refx = refx[:]

    incr = h / 20
    plotcell = cells.Range('J2')
    cell2 = cells.Range('L2')
    ref_m = D('0.005497')

    b_cell = cells.Range("M2")

    linest_range = cells.Range(cell2, b_cell)
    linest_formula = "=linest(%s,%s)"

    xcol = 10
    ycol = 11

    linest_range.Value = ((0.002, 0),)

    while D(cell2.Value) < ref_m:
        print("Plotting data with h=%s" % h)
        plot_m(h, linest_formula, linest_range, plotcell, xcol, ycol)
        sleep(0.2)
        h += incr

    incr /= 10

    while D(cell2.Value) > ref_m:
        print("Plotting data with h=%s" % h)
        plot_m(h, linest_formula, linest_range, plotcell, xcol, ycol)
        sleep(0.2)
        h -= incr

    return h


def plot_m(h, linest_formula, linest_range, plotcell, xcol, ycol):
    from scripts.run.temp_sim import TempSim
    from officelib.xllib.xladdress import cellRangeStr
    sim = TempSim(28, 19, 50, heat_constant=h)
    data = sim.iterate(30000)
    xs, ys = zip(*data)
    start = next(i for i, pv in enumerate(ys) if pv > 30)
    end = next((i for i, pv in enumerate(ys, start) if pv > 36), len(ys) - 1)
    assert ys[start] > 30
    assert ys[end] > 36
    xldata = [(str(x), str(y)) for x, y in zip(xs[start:end], ys[start:end])]
    plotxl_by_cell(xldata, plotcell)
    linest_args = linest_formula % (
        cellRangeStr(
            (2, ycol), (end - start, ycol)
        ),
        cellRangeStr(
            (2, xcol), (end - start, xcol)
        )
    )

    # print(linest_args)

    linest_range.FormulaArray = linest_args


join = '\\'.join


def dirwalk(dir):
    contents = listdir(dir)
    paths = []; path_append = paths.append
    for f in contents:
        path = join((dir, f))
        try:
            paths.extend(dirwalk(path))
        except OSError:
            path_append(path)
    return paths

# noinspection PyUnresolvedReferences
dirwalk = make_constants(listdir=listdir, OSError=OSError, join=join)(dirwalk)


def get_xl_data2():

    from officelib.xllib.xlcom import xlBook2
    from officelib.const import xlDown
    from pysrc.snippets import smooth1
    import re
    from itertools import takewhile
    xl, wb = xlBook2('PID.xlsx')
    ws = wb.Worksheets('p30')
    cells = ws.Cells

    # columns = (5, 9, 13, 17, 21, 25, 29)
    columns = range(2, 19, 4)

    parse_name = re.compile(r"p(\d*)i([\d\.]*)").match

    all_dat = []
    ap = all_dat.append
    row = 2

    def good(o):
        return o != (None, None)

    for col in columns:

        data = cells.Range(cells(row, col), cells(row, col + 1).End(xlDown)).Value
        name = cells(1, col + 1).Value
        xldata = takewhile(good, data)
        x, y = zip(*xldata)
        x_data, y_data = smooth1(x, y)

        p, i = parse_name(name).groups()
        ap(xlData(name, x_data, y_data, p, i))

    return all_dat
