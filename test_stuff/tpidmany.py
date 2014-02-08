"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

from officelib.pbslib.proxies import BatchFile, Parameter


manyfile = "C:\\Users\\PBS Biotech\\Downloads\\2014020613364723.csv"
manyfile2 = "C:\\Users\\PBS Biotech\\Downloads\\overnight2.csv"

def openbatch(file: str=manyfile) -> BatchFile:
    batch = BatchFile(file)
    return batch

from datetime import timedelta

def find_tests(batch: BatchFile):

    tempsp = batch['TempPV(C)']
    data = iter(tempsp)
    time, sp = next((t, s) for t, s in data if s >= 37)
    tests = [(time, sp)]
    test_time = timedelta(seconds=1200)
    while True:
        try:
            _endtime, _endsp = next((t + test_time, s) for t, s in data if s <= 37)

            time, sp = next((t, s) for t, s in data if t > _endtime)
        except StopIteration:
            break

        tests.append((time, sp))

    pgain = batch["TempHeatDutyControl.PGain(min)"]
    itime = batch["TempHeatDutyControl.ITime(min)"]
    dtime = batch["TempHeatDutyControl.DTime(min)"]

    for time, sp in tests:

        p = next(p for t, p in pgain if t > time)
        i = next(i for t, i in pgain if t > time)
        d = next(d for t, d in pgain if t > time)

        print(time, sp, p, i, d)




def main():

    batch = openbatch(manyfile2)

    # tempsp = batch['TempSP(C)']
    # lasttime, lastsp = tempsp[0]
    # tests = [(lasttime, lastsp)]
    # for time, sp in tempsp:
    #     if sp != lastsp:
    #         tests.append((time, sp))
    #         lasttime, lastsp = time, sp

    # for date, val in tests:
    #     print(date, val)

    find_tests(batch)


if __name__ == "__main__":
    main()

