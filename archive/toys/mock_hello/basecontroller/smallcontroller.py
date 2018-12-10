"""

Created by: Nathan Starkweather
Created on: 12/03/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


class SmallControllerModel():
    def __init__(self, name):
        self.name = name


class SmallControllerView():
    def __init__(self, name):
        self.name = name


class SmallControllerWidget():
    def __init__(self, name):
        self.model = SmallControllerModel(name)
        self.view = SmallControllerView(name)

