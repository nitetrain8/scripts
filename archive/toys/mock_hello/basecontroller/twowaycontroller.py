"""

Created by: Nathan Starkweather
Created on: 12/03/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


class TwoWayControllerView():
    def __init__(self, root, name):
        self.root = root
        self.name = name


class TwoWayControllerModel():
    def __init__(self, name):
        self.name = name


class TwoWayControllerWidget():
    def __init__(self, root, name):
        self.name = name
        self.view = TwoWayControllerView(root, name)
        self.model = TwoWayControllerModel(name)
