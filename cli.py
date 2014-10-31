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

if __name__ == '__main__':

    test2()
