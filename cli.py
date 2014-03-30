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


from opcode import opmap, opname, HAVE_ARGUMENT

LOAD_CONST = opmap['LOAD_CONST']
STORE_GLOBAL = opmap['STORE_GLOBAL']
EXTENDED_ARG = opmap['EXTENDED_ARG']
LOAD_GLOBAL = opmap['LOAD_GLOBAL']

GREATER_HAVE_ARG = HAVE_ARGUMENT - 1


def dummy_len(obj):
    print("Dummy len called")


def dummy_list(obj):
    print('Dummy list called')


builtin_dict = {'len': dummy_len,
                'list' : dummy_list}


def make_constants(f, builtins_only=False, ignore=None):
    """
    I forget the URL to where I found this recipe, but it should be easy to find
    I think I have it bookmarked.

    @param f:
    @type f: types.FunctionType
    @param builtins_only:
    @type builtins_only: bool
    @type ignore: dict
    @return:
    @rtype:
    """
    code = f.__code__
    newconstants = list(code.co_consts)
    newcode = list(code.co_code)
    names = code.co_names

    import builtins
    env = vars(builtins).copy()

    if builtins_only:
        pass
    else:
        env.update(f.__globals__)

    if ignore is not None:
        # todo
        pass

    codelen = len(newcode)
    i = 0
    while i < codelen:
        op = newcode[i]

        if op in (STORE_GLOBAL, EXTENDED_ARG):
            return f
        if op == LOAD_GLOBAL:
            oparg = newcode[i + 1]
            if newcode[i + 2] != 0:
                raise BaseException("Poor understanding of Python Bytecode!")
            name = names[oparg]
            if name in env:
                value = env[name]
                for pos, v in enumerate(newconstants):
                    if v is value:
                        break
                else:
                    pos = len(newconstants)
                    newconstants.append(value)
                newcode[i] = LOAD_CONST
                newcode[i + 1] = pos
                newcode[i + 2] = 0

        i += 1
        if op > GREATER_HAVE_ARG:
            i += 2

    newcode = type(code)(
        code.co_argcount,
        code.co_kwonlyargcount,
        code.co_nlocals,
        code.co_stacksize,
        code.co_flags,
        bytes(newcode),
        tuple(newconstants),
        code.co_names,
        code.co_varnames,
        code.co_filename,
        code.co_name,
        code.co_firstlineno,
        code.co_lnotab,
        code.co_freevars,
        code.co_cellvars
    )

    newfunc = type(f)(
        newcode,
        f.__globals__,
        f.__name__,
        f.__defaults__,
        f.__closure__
    )

    return newfunc


def testfoo():
    data = (1, 2, 3)
    len(data)
    list(data)
    for d in data:
        print(d, end='')


import pdb


def scancode(f):
    code = f.__code__
    codelen = len(code.co_code)
    co_code = code.co_code
    i = 0

    while i < codelen:
        op = co_code[i]

        if op == LOAD_GLOBAL:
            arg1 = co_code[i + 1]
            arg2 = (co_code[i + 2] << 8)
            oparg = arg1 + arg2
            print(oparg)
            if oparg != arg1:
                print(f.__qualname__, oparg, repr(arg1), repr(arg2))
                pdb.set_trace()
            if arg2 != co_code[i + 2]:
                print(arg2, f.__qualname__)

        i += 1
        if op > GREATER_HAVE_ARG:
            i += 2


from types import ModuleType, CodeType, FunctionType
import inspect


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

    from os import walk, listdir
    import builtins
    from pickle import PickleError

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

    before = Timer(testfoo2).timeit
    after = Timer(_make_constants(testfoo2)).timeit

    before_total = after_total = 0

    from itertools import count
    n=3
    for i in count(1):

        bresult = before(n)
        aresult = after(n)

        before_total += bresult
        after_total += aresult

        print()
        print("Before:", bresult, "After:", aresult)
        print("Before Total", before_total / i, "After Total:", after_total / i)
        print()


def find_func(name="PyMethod_New", fldr="Objects"):
    from os import listdir
    import re

    magic = re.compile(r"typedef .*?(%s)" % name).match

    fldr = "C:\\Users\\Administrator\\Downloads\\Python-3.4.0\\" + fldr
    fldr = "C:\\Python33\\include"
    for file in listdir(fldr):
        if file.endswith('.c') or file.endswith(".h"):
            fpath = '\\'.join((fldr, file))
            with open(fpath, 'r') as f:
                text = f.read()
            if name in text:
                print(file)
            match = magic(text)
            if match:
                print("magic!", file)
