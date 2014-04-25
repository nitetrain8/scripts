"""

Created by: Nathan Starkweather
Created on: 03/19/2014
Created in: PyCharm Community Edition


"""

# noinspection PyUnresolvedReferences
from scripts.old_cli import process, plot, plotpid, plotpid2, plotpid3, profile, xlData, \
    plotxl, cli_load, cli_store, get_ref_map, get_ref_data, reload, get_xl_data, reload2, \
    plotxl_by_cell, dirwalk
from decimal import Decimal as D


__author__ = 'Nathan Starkweather'


def delsim():
    import sys

    try:
        del sys.modules['scripts.run.temp_sim']
    except KeyError:
        pass


# noinspection PyUnusedLocal
def supermath3(delay=0, leak_constant=0, ref_data=None, i=D('0.5'), plot=True, p=40):
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
    # import queue
    # i = D(i) * 3 + D('13.95')

    pid_kwargs = {
        'set_point' : 37,
        'pgain': p,
        'itime': i,
        'out_high' : 100,
        'out_low' : -100,
        'ideal' : True
        }

    sim_kwargs = {
        'start_temp': (D('28.183')),
        'env_temp': 19,
        'delay': delay,
        'leak_const': leak_constant,

    }

    sim = TempSim(**sim_kwargs)
    pid = PIDController(**pid_kwargs)

    times, pvs, hds = process(sim, pid)

    if plot:
        fix = D('1')
        times = map(str, (t - fix for t in times))
        xldata = tuple(zip(times, map(str, pvs), map(str, hds)))
        cell1, cell2 = plotxl(xldata, 19, 2, "SimDataP%di%.1f" %
                              (pid_kwargs['pgain'],
                               pid_kwargs['itime']), "PID.xlsx", 2)

        wb = cell1.Parent.Parent
        ws = wb.Worksheets(1)
        cells = ws.Cells
        cells(11, 3).Value = str(p)
        cells(12, 3).Value = str(i)
        cells(8, 3).Value = str(delay)

        cells2 = wb.Worksheets("Calc").Cells
        cells2(2, 9).Value = str(sim_kwargs['env_temp'])
        cells2(4, 9).Value = str(sim_kwargs['start_temp'])

    # if ref_data is None:
    #     try:
    #         ref_data = get_ref_map()[str(i)]
    #         print(ref_data)
    #         ref_data = ref_data.y_data
    #     except:
    #         ref_data = get_ref_data()[0]
    #         print(ref_data)
    #         ref_data = ref_data.y_data

    # totaldiff = sum(map(abs, (r - p for r, p in zip(ref_data, pvs))))
    # print("Delay:", sim_kwargs['delay'], end=' ')
    # print("Totaldiff:", totaldiff, end=' ')
    # print("Ave_diff:", totaldiff / len(ref_data))

    # return totaldiff

    # plot(times, pvs, ref_data)
    # return times, pvs


def find_func(name="PyMethod_New", subdir=""):
    # from os import listdir

    # import re
    # magic = re.compile(r"typedef.*?(%s)" % name).match

    subdir = "D:\\Python-3.4.0\\" + subdir
    # fldr = "C:\\Python33\\include"
    dirs = dirwalk(subdir)
    # print(len(dirs))
    for i, fpath in enumerate(dirs):
        # if fpath.endswith('.py'):
            # fpath = '\\'.join((subdir, fpath))
        try:
            with open(fpath, 'r') as f:
                text = f.read().splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text, 1):
            if name in line:
                print(fpath, "Line number", lineno)

                    # match = magic(line)
                    # if match:
                    #     print("magic!", fpath)
                    #     break


def _run_test(p=40, i=1320, delay=0, leak_const=0):
    supermath3(delay=delay,
               leak_constant=leak_const,
               ref_data=None,
               i=i,
               plot=True,
               p=p)


def get_paired_cols(firstcell):
    from officelib.const.const import xlToRight, xlDown

    ws = firstcell.Parent
    cells = ws.Cells
    cell_range = cells.Range

    rightcell = firstcell.End(xlToRight)
    lastcell = rightcell.End(xlDown)

    xldata = cell_range(firstcell, lastcell).Value2
    return xldata


def test_cooling(c=D('-0.000039')):
    delsim()
    from scripts.run.temp_sim import TempSim

    sim = TempSim(42, 15, 0, c)
    steps = sim.iterate(40000)
    # _str = str
    # steps = [(_str(x), _str(y)) for x, y in steps]
    return steps


def run_test2(p=40, i=1320 / 60):
    _run_test(p, i)


# optimize_namespace(globals(), globals())
