"""

Created by: Nathan Starkweather
Created on: 03/19/2014
Created in: PyCharm Community Edition


"""
# noinspection PyUnresolvedReferences
from scripts.old_cli import process, plot, plotpid, plotpid2, plotpid3, profile, xlData, \
    plotxl, cli_load, cli_store, get_ref_map, get_ref_data, reload, get_xl_data, reload2
from decimal import Decimal as D

__author__ = 'Nathan Starkweather'


def delsim():
    import sys

    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass


# noinspection PyUnusedLocal
def supermath3(delay=0, leak_constant=0, ref_data=None, i=D('0.5'), ifactor=D(1), plot=True):
    """
    @param delay:
    @type delay: int | Decimal
    @param leak_constant:
    @type leak_constant: int | Decimal
    @return:
    @rtype:
    """
    delsim()
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
        # 'cool_constant': TempSim.cooling_constant,
        # 'heat_constant': TempSim.heating_constant,
        'delay': delay,
        'leak_const': leak_constant
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

    return totaldiff

    # plot(times, pvs, ref_data)
    # return times, pvs


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
        while diff:

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


import operator
import sys
g = sys.modules['__main__'].__dict__


# noinspection PyGlobalUndefined
def run_test(op=operator.add, amt=0.2, itime=2.5):

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
