"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

from officelib.pbslib.proxies import BatchFile, Parameter


manyfile = "C:\\Users\\PBS Biotech\\Downloads\\2014020613364723.csv"


def openbatch(file: str=manyfile) -> BatchFile:
    batch = BatchFile(file)
    return batch


def find_tests(param: Parameter):

    data = iter(param)
    time, sp = next((t, s) for t, s in data if s == 37)
    tests = [(time, sp)]

    while True:
        try:
            _endtime, _endsp = next((t, s) for t, s in data if s == 39)
            time, sp = next((t, s) for t, s in data if s == 37)
        except StopIteration:
            break

        tests.append((time, sp))

    for time, sp in tests:
        print(time, sp)



def main():

    batch = openbatch()
    tempsp = batch['TempSP(C)']
    lasttime, lastsp = tempsp[0]
    tests = [(lasttime, lastsp)]
    for time, sp in tempsp:
        if sp != lastsp:
            tests.append((time, sp))
            lasttime, lastsp = time, sp

    for date, val in tests:
        print(date, val)

    find_tests(tempsp)


if __name__ == "__main__":
    main()

