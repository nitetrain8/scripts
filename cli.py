"""

Created by: Nathan Starkweather
Created on: 10/29/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


def test():
    from hello.repl import analyze_batches
    import subprocess
    subprocess.call("tskill.exe EXCEL")

    return analyze_batches()


def test2():
    import hello.kla
    import subprocess

    subprocess.call("tskill.exe EXCEL")
    hello.kla.__test_analyze_kla()

from itertools import zip_longest


def simplediff(t1, t2):
    """
    @type t1: str
    @type t2: str
    @return:
    """
    wds1 = t1.split()
    wds2 = t2.split()

    for i, (w1, w2) in enumerate(zip(wds1, wds2)):
        if w1 != w2:
            print("DIFF line %d: %s != %s" % (i, w1, w2), end='')
            if w1.lower() == w2.lower():
                print("MISMATCHED CASE")
            else:
                for c1, c2 in zip_longest(w1, w2, fillvalue="<empty>"):
                    if c1 != c2:
                        print(" ", c1, "!=", c2, "(%d != %d)" % (ord(c1), ord(c2)))


def tkquickdiff():
    import tkinter as tk
    import tkinter.ttk as ttk
    import difflib

    root = tk.Tk()
    frame = ttk.LabelFrame(root)
    e1 = ttk.Entry(frame)
    e2 = ttk.Entry(root)

    def dodiff():
        txt1 = e1.get()
        txt2 = e2.get()
        simplediff(txt1, txt2)

    button = ttk.Button(frame, text="Diff", command=dodiff)

    button.grid()
    e1.grid()
    e2.grid()
    frame.grid()
    root.mainloop()


def c():
    print("C")
    from hello.mock.server import _stack_trace
    for line in (_stack_trace()):
        print(line)


def b():
    print("B")
    c()


def a():
    print("A")
    b()


def foo():
    a()

if __name__ == '__main__':

    foo()
