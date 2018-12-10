"""

Created by: Nathan Starkweather
Created on: 12/03/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import tkinter as tk
import tkinter.ttk as ttk
from scripts.toys.mock_hello.state import HelloInterface

def run_test():
    root = tk.Tk()
    lf = ttk.LabelFrame(root, text="Foo")
    label = ttk.Label(lf, text="barbar")
    lf.grid()
    label.grid()
    return root

if __name__ == '__main__':
    run_test()
