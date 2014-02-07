"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


class MyClass():

    def __init__(self, iterable):
        self._list = list(iterable)

    def __iter__(self):
        for val in self._list:
            yield val


m = MyClass(range(100))
