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
    analyze_batches()

if __name__ == '__main__':
    test()
