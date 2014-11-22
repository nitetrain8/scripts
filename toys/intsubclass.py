"""

Created by: Nathan Starkweather
Created on: 11/20/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

class MyInt(int):
    def __add__(self, other):
        val = int.__add__(self, other)
        return MyInt(val)

myint = MyInt

def main():
    one = MyInt(1)
    two = myint(2)
    print(type(one))
    print(type(two))
    print(type(one + two))



if __name__ == '__main__':
    main()
