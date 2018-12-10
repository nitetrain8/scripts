"""

Created by: Nathan Starkweather
Created on: 12/03/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import tkinter as tk
import tkinter.ttk as ttk


class DisplayLabel():
    """
    A simple compound widget consisting of two Label widgets:
    one fixed (the "label") and one dynamic ("display").
    """
    def __init__(self, root, text):
        self.frame = tk.Frame(root)
        self.label = tk.Label(self.frame, text=text)
        self.tv = tk.StringVar()
        self.display = tk.Label(self.frame, textvariable=self.tv)

    def set_label(self, text):
        self.label.configure(text=text)

    def update(self, text):
        self.tv.set(text)

    def grid(self, row, col):
        self.frame.grid(row=row, column=col)
        self.label.grid(0, 0)
        self.display.grid(0, 1)
