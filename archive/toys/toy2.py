"""

Created by: Nathan Starkweather
Created on: 02/28/2014
Created in: PyCharm Community Edition


"""


def list1(iterable):
    foo = []
    append = list.append
    for v in iterable:
        append(foo, v)
    return foo

def list2(iterable):
    foo = [v for v in iterable]
    return foo

loops = 1000000
from time import perf_counter as timer

t1 = timer()
list1(range(loops))
t2 = timer()

t3 = timer()
list2(range(loops))
t4 = timer()

print("List1: ", t2-t1)
print("List2: ", t4-t3)
