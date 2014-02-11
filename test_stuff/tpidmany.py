"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

from officelib.pbslib.proxies import BatchFile
from itertools import zip_longest
from collections import OrderedDict
from officelib.xllib.xladdress import cellRangeStr
from officelib.pbslib.batchutil import ParseDateFormat


manyfile = "C:\\Users\\PBS Biotech\\Downloads\\2014020613364723.csv"
manyfile2 = "C:\\Users\\PBS Biotech\\Downloads\\overnight2.csv"
manypickle = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\scripts\\test_stuff\\manyfile.txt"
manyfile3 = "C:\\Users\\PBS Biotech\\Downloads\\overweekend.csv"
manyrecipesteps = "C:\\Users\\PBS Biotech\\Downloads\\weekendsteps.csv"


def openbatch(file: str=manyfile) -> BatchFile:
    batch = BatchFile(file)
    return batch

from datetime import timedelta, datetime


class TempRamp():
    def __init__(self,
                pgain: float,
                itime: float,
                dtime: float,
                start_time: datetime,
                end_time: datetime,
                start_index: int,
                end_index: int):
        self.pgain = pgain
        self.itime = itime
        self.dtime = dtime
        self.start_time = start_time
        self.end_time = end_time
        self.start_index = start_index
        self.end_index = end_index

    def __str__(self) -> str:
        out = """Temp PID Test:
        P gain: {0} I time: {1} D time: {2}

        Start time: {3}
        End time: {4}

        Excel line index:
        Start: {5}, End: {6}
        """

        out = out.format(self.pgain, self.itime, self.dtime,
                         self.start_time, self.end_time,
                         self.start_index + 2, self.end_index + 2)
        return out


def backup_settings() -> list:
    """
    @return: list of settings with constant
             ratio.
    """
    ps = [5 * i for i in range(1, 10)]
    settings = ((p, p / 10, 0) for p in ps)
    return list(settings)


def find_settings(batch: BatchFile, tests: list):
    #
    pgain = batch["TempHeatDutyControl.PGain(min)"]
    itime = batch["TempHeatDutyControl.ITime(min)"]
    dtime = batch["TempHeatDutyControl.DTime(min)"]

    info = []
    for start_index, end_index, start, end in tests:
        p = next(pv for t, pv in pgain if t > start)
        i = next(pv for t, pv in itime if t > start)
        d = next(pv for t, pv in dtime if t > start)

        test = TempRamp(p, i, d, start, end, start_index, end_index)

        info.append(test)

    return info


def hardmode_auto2auto(batch: BatchFile):

    temppv = batch['TempPV(C)']
    data = iter(temppv)
    settle_time = timedelta(seconds=1200)

    tests = []
    start_index = 0
    start, temp = next(data)
    end_index, end = next((i, time) for i, (time, pv) in enumerate(data, start=1) if pv > 39)
    end += settle_time
    end_index , end = next((i, time) for i, (time, pv) in enumerate(data, start=end_index + 1) if time > end)

    tests.append((start_index, end_index, start, end))
    while True:

        # This loop sucks. For each set of points, need to call next() twice. First to find where
        # temp pv crosses the line to indicate the next step in the recipe, second to
        # find the timestamp after waiting the 1200 second settle time.
        try:
            start_index, start = next((i, time) for i, (time, pv) in enumerate(data, start=end_index + 1) if pv < 37)
            start += settle_time
            start_index, start = next((i, time) for i, (time, pv) in enumerate(data, start=start_index + 1) if time > start)

            end_index, end = next((i, time) for i, (time, pv) in enumerate(data, start=start_index + 1) if pv > 39)
            end += settle_time
            end_index, end = next((i, time) for i, (time, pv) in enumerate(data, start=end_index + 1) if time > end)
        except StopIteration:
            break
        tests.append((start_index, end_index, start, end))

    return tests


def find_full_tests(filename: str):

    with open(filename, 'r') as f:
        f.readline()
        contents = [line.strip().split(',') for line in f.readlines()]

    tests = []
    data = iter(contents)

    while True:
        try:
            start = next(time for _, time, step in data if step == 'Set "TempModeUser" to Auto')
            auto_start = next(time for _, time, step in data if step == 'Wait 5 seconds')
            end = next(time for _, time, step in data if step == 'Set "TempModeUser" to Off')
        except StopIteration:
            break
        tests.append((start, auto_start, end))

    parse = ParseDateFormat
    s = datetime.strptime
    parsed = []
    for start, auto_start, end in tests:
        fmt = parse(start)
        parsed.append((s(start, fmt), s(auto_start, fmt), s(end, fmt)))

    for test in parsed:
        print(test)


def unpickle_info(filename: str) -> object:
    from pickle import load as pickle_load
    with open(filename, 'rb') as f:
        info = pickle_load(f)
    return info


def pickle_info(info: object, filename: str):

    from pysrc.snippets import safe_pickle
    safe_pickle(info, filename)


def process_info(info: list, batch: BatchFile=None):

    if batch is None:
        batch = unpickle_info(manypickle)
        # noinspection PyTypeChecker
        batch = BatchFile.fromMapping(batch)

    temppv = batch['TempPV(C)']
    pv_times = temppv.Times.Datestrings
    pv_values = temppv.Values
    datas = []
    for t in info:
        start_index = t.start_index
        end_index = t.end_index
        times = pv_times[start_index:end_index]
        values = pv_values[start_index:end_index]
        datas.extend([times, values, (None,), (None,)])

    columns = len(datas)
    datas = list(zip_longest(*datas))
    rows = len(datas)

    row1 = []
    row2 = []
    for t in info:
        row1.extend(('Pgain', 'Itime', 'Dtime', None))
        row2.extend((t.pgain, t.itime, t.dtime, None))
    start_row = 3
    data_area = cellRangeStr(
                        (start_row, 1),
                        (rows + start_row, columns)
                        )

    row1_area = cellRangeStr(
                            (1, 1),
                            (1, len(row1))
                            )
    row2_area = cellRangeStr(
                            (2, 1),
                            (2, len(row2))
                            )
    from officelib.xllib.xlcom import xlObjs
    xl, wb, ws, cells = xlObjs(visible=False)

    try:
        cells.Range(row1_area).Value = row1
        cells.Range(row2_area).Value = row2
        cells.Range(data_area).Value = datas
    finally:
        xl.Visible = True


def main(filename: str) -> list:

    batch = openbatch(filename)
    tests = hardmode_auto2auto(batch)
    info = find_settings(batch, tests)
    pickle_file = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\scripts\\test_stuff\\test_output.txt"
    pickle_info(info, pickle_file)
    pickle_info(OrderedDict(batch), manypickle)
    return info, batch


def main2(batch_filename: str, recipe_filename: str) -> list:
    find_full_tests(recipe_filename)

if __name__ == "__main__":

    main2(manyfile3, manyrecipesteps)
    # info = unpickle_info(file)
    # info, batch = main(manyfile3)
    #
    # # noinspection PyTypeChecker
    # process_info(info, batch)
