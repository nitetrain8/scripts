"""

Created by: Nathan Starkweather
Created on: 12/03/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


class PIDLoopView():
    def __init__(self):
        pass


class PIDLoopModel():
    def __init__(self, pgain, itime, dtime):
        self.pgain = pgain
        self.itime = itime
        self.dtime = dtime


class PIDLoopWidget():
    def __init__(self, pgain, itime, dtime):
        self.model = PIDLoopModel(pgain, itime, dtime)
        self.view = PIDLoopView
