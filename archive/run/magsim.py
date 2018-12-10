"""

Created by: Nathan Starkweather
Created on: 05/21/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


def reloadmag():
    import sys

    paths = 'magsim', 'run.magsim', 'scripts.run.magsim'
    for path in paths:
        try:
            del sys.modules[path]
        except KeyError:
            pass

    _g = sys.modules['__main__'].__dict__
    impcmd = "from scripts.run.magsim import *"
    exec(impcmd, _g, _g)


from decimal import Decimal

# Aliases for convenience, since this script should be REPL friendly
decimal = Decimal
D = Decimal


class SimplePID():

    # Off mode is actually a special case of manual mode where SP = 0
    AUTO_MODE = 0
    MAN_MODE = OFF_MODE = 1
    RANGE_MIN = D(0)
    RANGE_MAX = D(100)

    def __init__(self, p=D('0.5'), i=D('0.1'), d=D(0), step_interval=D('0.3')):
        self.p = D(p)
        self.i = D(i)
        if self.i != 0:
            self.oneoveri = 1 / self.i
        else:
            self.oneoveri = D(0)
        self.d = D(d)
        self.step_interval = D(step_interval)
        self.accumulated_error = D(0)
        self.mode = 1
        self.bump = D(0)
        self.man_sp = 0
        self.auto_sp = 0
        self.last_pv = 0

    def set_mode_auto(self, pv=0, sp=0):
        if self.mode == self.MAN_MODE:
            self.bump = self.man_sp - self.p * D(sp - pv)
        self.mode = self.AUTO_MODE
        self.auto_sp = 0
        self.last_pv = 0

    def set_mode_off(self):
        self.mode = self.MAN_MODE
        self.bump = 0
        self.accumulated_error = D(0)

    def set_mode_man(self, sp):
        self.mode = self.MAN_MODE
        self.bump = 0
        self.accumulated_error = D(0)

        if sp > self.RANGE_MAX:
            self.man_sp = self.RANGE_MAX
        elif sp < self.RANGE_MIN:
            self.man_sp = self.RANGE_MIN
        else:
            self.man_sp = sp

    def step(self, pv):
        if self.mode == self.MAN_MODE:
            return self.man_sp

        e = self.auto_sp - pv
        self.accumulated_error += e * self.step_interval

        op = self.p * (e + self.oneoveri * self.accumulated_error + self.d * (pv - self.last_pv))

        self.last_pv = pv

        return op


def coroutine(f):

    def _coroutine(*args, **kwargs):
        r = f(*args, **kwargs)
        next(r)
        return r.send
    return _coroutine


@coroutine
def output_throttle(maxrate=D('0.1'), start=0):
    if maxrate < 0:
        raise ValueError("Maxrate cannot be less than 0")
    if maxrate == 0:
        maxrate = 10000

    minrate = -maxrate

    op = lastop = D(start)
    while True:
        op = yield op
        rate = op - lastop

        if rate > maxrate:
            op = lastop + maxrate
        elif rate < minrate:
            op = lastop + minrate

        lastop = op




