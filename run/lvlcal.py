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

    def span(self, x, y):
        x1 = - self.b / self.m

        newm = y / (x - x1)
        newb = y - newm * x

        self.m = newm
        self.b = newb

    def __repr__(self):
        return "m: %.2f b: %.2f" % (self.m, self.b)

    __str__ = __repr__
