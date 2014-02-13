"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

list1 = ["r1c%d" % i for i in range(10)]
list2 = ["r2c%d" % i for i in range(10)]
list3 = ["r3c%d" % i for i in range(10)]

from itertools import zip_longest

# list4 = []
# list4.extend((list1, list2, list3))
# print(list4)


list5 = [
        ["r1c1", "r1c2"],
        ["r2c1", "r2c2"],
        ["r3c1", "r3c2"]]
# 
# for i in range(2, 10, 2):
#     for n, row in enumerate(list5, start=1):
#         row.extend(("r%dc%d" % (n, i), "r%dc%d" % (n, i + 1)))
#     
# for i in list5:
#     print(i)

class myclass():
    def __enter__(self):
        print("enter")
    def __exit__(self, *args):
        if any(args):
            print(*args)
            print(args[0], args[1], args[2])
        print('exit')

try:
    with myclass() as m:
        raise ValueError
        print("hello world!")
except ValueError:
    pass
