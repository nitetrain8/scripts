"""

Created by: Nathan Starkweather
Created on: 12/03/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

try:
    from .basecontroller.smallcontroller import SmallControllerWidget
    from .basecontroller.standardcontroller import StandardControllerWidget
    from .basecontroller.twowaycontroller import TwoWayControllerWidget
except ImportError:
    from scripts.toys.mock_hello.basecontroller.smallcontroller import SmallControllerWidget
    from scripts.toys.mock_hello.basecontroller.standardcontroller import StandardControllerWidget
    from scripts.toys.mock_hello.basecontroller.twowaycontroller import TwoWayControllerWidget

import tkinter as tk, tkinter.ttk as ttk


class AgitationControllerWidget(StandardControllerWidget):
    def __init__(self, root):
        StandardControllerWidget.__init__(self, root, "Agitation")


class TemperatureControllerWidget(StandardControllerWidget):
    def __init__(self, root):
        StandardControllerWidget.__init__(self, root, "Temperature")


class DOControllerWidget(TwoWayControllerWidget):
    def __init__(self, root):
        TwoWayControllerWidget.__init__(self, root, "DO")


class pHControllerWidget(TwoWayControllerWidget):
    def __init__(self, root):
        TwoWayControllerWidget.__init__(self, root, "pH")


class HelloDashboard():
    def __init__(self, root):
        self.frame = ttk.LabelFrame(root, text="Dashboard")
        self.agitation = AgitationControllerWidget(self.frame)
        self.temperature = TemperatureControllerWidget(self.frame)
        self.do = DOControllerWidget(self.frame)
        self.pH = pHControllerWidget(self.frame)

    def grid(self, row, col):
        self.frame.grid(row=row, column=col)
        self.agitation.grid(0, 0)
        self.temperature.grid(1, 0)
        self.do.grid(2, 0)
        self.pH.grid(3, 0)


class HelloInterface():
    def __init__(self):

        self.root = tk.Tk("HELLO")
        # self.dashboard_frame
        self.agitation = AgitationControllerWidget(self.root)
        self.temperature = TemperatureControllerWidget(self.root)
        self.do = DOControllerWidget(self.root)
        self.pH = pHControllerWidget(self.root)

    def grid(self):
        self.agitation.grid(0, 0)
        self.temperature.grid(0, 0)
        self
