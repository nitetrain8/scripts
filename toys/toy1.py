"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""

__author__ = 'Nathan Starkweather'


class Class1():
    def foo(self):
        print("Foo Class1")

    def bar(self):
        self.foo()
        print("Bar Class1")

class Class2(Class1):
    def __init__(self):
        def bar(self):
            super().foo()
            print("Bar Class2")
        import types
        self.bar = types.MethodType(bar, self)

class Class25():
    def foo(self):
        print("Not this foo")
    def bar(self):
        print("Not this bar")

class Class3(Class25):
    def __init__(self):
        self.kls = Class2()
        def bar(self):
            super(self).foo()
            print("Bar Class2")

        import types

        self.kls.bar = types.MethodType(bar, self.kls)


if __name__ == '__main__':
    Class3().kls.bar()
