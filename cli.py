"""

Created by: Nathan Starkweather
Created on: 03/19/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


from decimal import Decimal as d

D = d


def y_of_t(tf, y0=d(25), incr=d(1), Kp=d('2.47938'), A=D('5'), tp=D(22000)):
    tf = d(tf)
    y0 = d(y0)
    incr = d(incr)
    Kp = d(Kp)
    A = d(A)
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


# def reload2():
#     print('bar')
#     import sys
#     try:
#         del sys.modules['scripts.cli']
#     except:
#         pass
#     from scripts import cli as _cli
#     sys.modules['scripts.cli'] = _cli
#     _g = {k : v for k, v in globals().items() if not k.startswith('__')}
#     sys.modules['__main__'].__dict__.update(_g)
#     sys.modules['__main__'].__dict__['reload'] = _cli.reload
