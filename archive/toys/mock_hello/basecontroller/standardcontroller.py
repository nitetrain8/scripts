"""

Created by: Nathan Starkweather
Created on: 12/03/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

# noinspection PyUnresolvedReferences
from .misc_widgets import DisplayLabel
import tkinter as tk


class StandardControllerView():
    def __init__(self, root, name):
        self.frame = tk.Frame(root)
        self.name = name

        self.pv = DisplayLabel(self.frame, "PV:")
        self.pv.update("0")
        self.sp = DisplayLabel(self.frame, "SP:")
        self.sp.update("0")
        self.mode = DisplayLabel(self.frame, "Mode")
        self.mode.update("Off")

    def grid(self, row, col):
        self.frame.grid(row=row, column=col)
        self.pv.grid(0, 0)
        self.sp.grid(1, 0)
        self.mode.grid(2, 0)


class StandardControllerModel():
    def __init__(self, name):
        self.name = name


class StandardControllerWidget():
    def __init__(self, root, name):
        self.view = StandardControllerView(root, name)
        self.model = StandardControllerModel(name)

    def grid(self, row, col):
        self.view.grid(row, col)
