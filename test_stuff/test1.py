"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMainWindow
from PyQt5.Qt import *
from sys import path as sys_path
sys_path.append("C:/Users/Administrator/Documents/Programming/python/pysrc")
from snippets import printdir
from sys import argv
app = QApplication(argv)
window = QMainWindow()
window.show()

env = QProcessEnvironment.systemEnvironment()
printdir(env)
list_ = env.toStringList()
for s in sorted(list_):
    print(s)

