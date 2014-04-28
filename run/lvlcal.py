"""

Created by: Nathan Starkweather
Created on: 04/24/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


def reloadcal():
    import sys
    del sys.modules['scripts.run.lvlcal']
    g = sys.modules['__main__'].__dict__
    exec("from scripts.run.lvlcal import *", g, g)


def calc_regression(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2

    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return m, b


class LvlCal():

    def __init__(self, m=5000, b=0):
        self.m = m
        self.b = b

    def zero(self, x):
        self.b -= x

    def zero2(self, x):
        x2 = x + 1
        y2 = self.calcy(x2)

        m, b = calc_regression((x, 0), (x2, y2))
        self.m = m
        self.b = b

    def span(self, x, y):
        """
        Span is performed by "rotating" the calibration around
        the zero point, ie the point at which y = 0 (x intercept).

        The new m and b should be calculated by finding the regression
        equation between the new (x, y) coordinate, and the x intercept,
        which is given by (-b/m, 0).

        @param x: x
        @type x: float | int
        @param y: y
        @type y: float | int
        @return: None
        @rtype: None
        """

        xint = (-self.b / self.m, 0)
        newm, newb = calc_regression(xint, (x, y))

        self.m = newm
        self.b = newb

    def calcy(self, x):
        return self.m * x + self.b

    def __repr__(self):
        return "m: %.2f b: %.2f" % (self.m, self.b)

    __str__ = __repr__
