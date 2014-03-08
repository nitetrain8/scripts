"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""

__author__ = 'Nathan Starkweather'


if __name__ == '__main__':
    from sys import getsizeof as sizeof
    from datetime import datetime
    foo = [datetime(2013, 1, 1) for i in range(1000)]
    print(sizeof(foo))
    print(sizeof(foo[1:]))
    print(sizeof)
    # print(sizeof(list()))
