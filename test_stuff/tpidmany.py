"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

from officelib.pbslib.proxies import BatchFile
from itertools import zip_longest
from collections import OrderedDict
from officelib.pbslib.batchutil import ParseDateFormat, flatten
from weakref import ref as wref
from datetime import timedelta, datetime
from officelib.xllib.xladdress import cellStr, cellRangeStr

manyfile = "C:\\Users\\PBS Biotech\\Downloads\\2014020613364723.csv"
manyfile2 = "C:\\Users\\PBS Biotech\\Downloads\\overnight2.csv"
manypickle = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\scripts\\test_stuff\\manyfile.txt"
manyfile3 = "C:\\Users\\PBS Biotech\\Downloads\\overweekend.csv"
manyrecipesteps = "C:\\Users\\PBS Biotech\\Downloads\\weekendsteps.csv"
pickle_cache = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\scripts\\test_stuff\\pickle_cache"


def open_batch(file: str=manyfile) -> BatchFile:
    batch = BatchFile(file)
    return batch


class RampTest():
    def __init__(self,
                pgain: float=0,
                itime: float=0,
                dtime: float=0,
                start_time: datetime=None,
                end_time: datetime=None,
                start_index: int=0,
                end_index: int=0,
                test_name: str="Temp PID Test"):
        """
        @param pgain: pgain value
        @type pgain: float
        @param itime: itime value
        @type itime: float
        @param dtime: dtime value
        @type dtime: float
        @param start_time: start time as a datetime.datetime instance
        @type start_time: datetime.datetime
        @param end_time: end time as a datetime.datetime instance
        @type end_time: datetime.datetime
        @param start_index: PYTHON start index in corresponding data column
        @type start_index: int
        @param end_index: PYTHON start index in corresponding data column
        @type end_index: int
        """
        self.pgain = pgain
        self.itime = itime
        self.dtime = dtime
        self.start_time = start_time
        self.end_time = end_time
        self.start_index = start_index
        self.end_index = end_index
        self.test_name = test_name

    @property
    def DataRef(self):
        return self._data_ref()

    @DataRef.setter
    def DataRef(self, data):
        """
        @param data: T
        @type data:
        @return:
        @rtype:
        """
        self._data_ref = wref(data)

    def __repr__(self) -> str:
        """
        @return: human readable representation. For debugging/interactive console use.
        """

        out = """
        {7}:
        P gain: {0} I time: {1} D time: {2}

        Start time: {3}
        End time: {4}

        Excel line index:
        Start: {5}, End: {6}
        """.format(self.pgain, self.itime, self.dtime,
                         self.start_time, self.end_time,
                         self.start_index + 2, self.end_index + 2,
                         self.test_name)
        return out


class ChartInfo():
    def __init__(self,
                 series_name=None,
                 start_row=None,
                 end_row=None,
                 x_column=None,
                 y_column=None,
                 sheet_name=None):

        self.series_name = series_name
        self.start_row = start_row
        self.end_row = end_row
        self.x_column = x_column
        self.y_column = y_column
        self.sheet_name = sheet_name

    @property
    def XSeriesRange(self, cellRangeStr=cellRangeStr):
        return "=%s!" % self.sheet_name + cellRangeStr(
                                                    (self.start_row, self.x_column, 1, 1),
                                                    (self.end_row, self.x_column, 1, 1)
                                                    )

    @property
    def YSeriesRange(self, cellRangeStr=cellRangeStr):
        return "=%s!" % self.sheet_name + cellRangeStr(
                                                    (self.start_row, self.y_column, 1, 1),
                                                    (self.end_row, self.y_column, 1, 1)
                                                    )

    @property
    def SeriesName(self):
        return self.series_name


def backup_settings() -> list:
    """
    @return: list of settings with constant
             ratio.
    """
    ps = [5 * i for i in range(1, 10)]
    settings = ((p, p / 10, 0) for p in ps)
    return list(settings)


def find_auto2auto_settings(batch: BatchFile, tests: list):

    pgain = batch["TempHeatDutyControl.PGain(min)"]
    itime = batch["TempHeatDutyControl.ITime(min)"]
    dtime = batch["TempHeatDutyControl.DTime(min)"]

    info = []
    for start_index, end_index, start, end in tests:
        p = next(pv for t, pv in pgain if t > start)
        i = next(pv for t, pv in itime if t > start)
        d = next(pv for t, pv in dtime if t > start)

        test = RampTest(p, i, d, start, end, start_index, end_index)

        info.append(test)

    return info


def hardmode_auto2auto_tests(batch: BatchFile):

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


def find_full_tests(steps_report: str) -> list:
    """
    @param steps_report: filename of batch report listing recipe steps
    @type steps_report: str
    @return: list of Off-to-auto start, auto-to-auto start
    @rtype: list[(datetime, datetime, datetime)]
    """

    with open(steps_report, 'r') as f:
        f.readline()
        contents = [line.strip().split(',') for line in f.readlines()]

    tests = []
    data = iter(contents)

    while True:
        try:
            off_start = next(time for _, time, step in data if step == 'Set "TempModeUser" to Auto')
            auto_start = next(time for _, time, step in data if step == 'Wait 5 seconds')
            auto_end = next(time for _, time, step in data if step == 'Set "TempModeUser" to Off')
        except StopIteration:
            break

        tests.append((off_start, auto_start, auto_end))

    # The recipe steps report gives inaccurate timestamps,
    # so we need to fix it by adding one hour.
    parse_fmt = ParseDateFormat
    strptime = datetime.strptime
    parsed = []

    for off_start, auto_start, auto_end in tests:
        fmt = parse_fmt(off_start)
        off_start = strptime(off_start, fmt)
        auto_start = strptime(auto_start, fmt)
        auto_end = strptime(auto_end, fmt)
        parsed.append((off_start, auto_start, auto_end))

    return parsed


def unpickle_info(filename: str):
    from pickle import load as pickle_load
    with open(filename, 'rb') as f:
        info = pickle_load(f)

    if isinstance(info, OrderedDict):
        info = BatchFile.fromMapping(info)

    return info


def pickle_info(info: object, filename: str):

    from pysrc.snippets import safe_pickle

    if isinstance(info, BatchFile):
        info = OrderedDict(info)

    safe_pickle(info, filename)


def _make_elapsed(ref_cell, target_column, rows):
    """
    @param ref_cell: reference cell to use for elapsed time column
    @type ref_cell: (int, int)
    @param target_column: start cell for elapsed time column
    @type target_column: int
    @param rows: number of rows
    @type rows: int
    @return: list of formulas in r1c1 style (autoconverted by excel)
    @rtype: list[str]
    """
    ref_row, ref_col = ref_cell
    offset = ref_col - target_column  # offset should be negative if col > ref_col
    formula = "=(RC[{0}] - R{1}C{2}) * 1440".format(offset, ref_row, ref_col)

    return [formula for _ in range(rows)]


def process_tests(test_list, batch: BatchFile):
    """
    @param test_list: list of tests to process
    @type test_list: list[RampTest]
    @param batch: batch file corresponding to test list
    @type batch: BatchFile
    @ retu rn xl, wb, ws, cells
    @ rtyp e (T, U, V, X)
    """

    temppv = batch['TempPV(C)']
    pv_times = temppv.Times.Datestrings
    pv_values = temppv.Values

    magic_name_formula = '=CONCATENATE("p",R[2]C[-1],"I",R[2]C,"d",R[2]C[1])'
    columns_per_test = 5  # including blank spacer
    data_start_row = 11
    header_row_offset = 6

    # Todo- using a bunch of lists for rows is sloppy, but easiest way to
    # avoid having to transpose the whole header.
    datas = []
    row1 = []
    row2 = []
    row3 = []
    row4 = []
    chart_list = []
    for n, test in enumerate(test_list):

        start_index = test.start_index
        end_index = test.end_index
        times = pv_times[start_index:end_index]
        values = pv_values[start_index:end_index]

        column = n * columns_per_test + 1
        ref_cell = (data_start_row, column)
        rows = len(times)
        elapsed_times = _make_elapsed(ref_cell, column + 1, rows)

        chart_info = ChartInfo()
        chart_info.series_name = "=Sheet1!" + cellStr(1, column + 1)
        chart_info.start_row = data_start_row
        chart_info.end_row = data_start_row + rows - 1
        chart_info.x_column = column + 1
        chart_info.y_column = column + 2
        chart_list.append(chart_info)

        datas.extend([times, elapsed_times, values, (None,), (None,)])  # Need iterable placeholders for zip_longest
        row1.extend((test.test_name, magic_name_formula, None, None, None))
        row2.extend(('Pgain', 'Itime', 'Dtime', None, None))
        row3.extend((test.pgain, test.itime, test.dtime, None, None))
        row4.extend(("Test Time", "Elapsed Time", "TempPV(C)", None, None))

    columns = len(datas)
    datas = list(zip_longest(*datas))
    rows = len(datas)

    data_area = cellRangeStr(
                            (data_start_row, 1),
                            (rows + data_start_row - 1, columns)
                            )
    row1_area = cellRangeStr(
                            (1 + header_row_offset, 1),
                            (1 + header_row_offset, len(row1))
                            )
    row2_area = cellRangeStr(
                            (2 + header_row_offset, 1),
                            (2 + header_row_offset, len(row2))
                            )
    row3_area = cellRangeStr(
                            (3 + header_row_offset, 1),
                            (3 + header_row_offset, len(row3))
                            )
    row4_area = cellRangeStr(
                            (4 + header_row_offset, 1),
                            (4 + header_row_offset, len(row4))
                            )

    from officelib.xllib.xlcom import xlObjs, CreateChart, CreateDataSeries
    from officelib.const import xlR1C1, xlA1, xlXYScatterLinesNoMarkers

    xl, wb, ws, cells = xlObjs(visible=False)
    xl.ReferenceStyle = xlR1C1
    try:
        cells.Range(row1_area).Value = row1
        cells.Range(row2_area).Value = row2
        cells.Range(row3_area).Value = row3
        cells.Range(row4_area).Value = row4
        cells.Range(data_area).Value = datas

        chart = CreateChart(ws, xlXYScatterLinesNoMarkers)
        for series in chart.SeriesCollection():
            series.Delete()

        ws_name = ws.Name

        for info in chart_list:
            info.sheet_name = ws_name
            CreateDataSeries(chart, info.XSeriesRange, info.YSeriesRange, info.SeriesName)

    finally:
        xl.ReferenceStyle = xlA1
        xl.Visible = True


def find_all_tests(tests: list, batch: BatchFile) -> list:
    """
    @param tests: list of tests (start, end1, start2, end2) datetimes
    @type tests: list[(datetime, datetime, datetime)]
    @param batch: batch file corresponding to tests
    @param batch: BatchFile
    @return: list of tests with indicies.
    @rtype: list[(RampTest, RampTest, RampTest)]

    This process is rather different than the Auto2Auto settings finder,
    so needs its own implementation despite identical code in some places.
    """
    pgain = batch["TempHeatDutyControl.PGain(min)"]
    itime = batch["TempHeatDutyControl.ITime(min)"]
    dtime = batch["TempHeatDutyControl.DTime(min)"]
    temp_times = iter(batch["TempPV(C)"].Times)
    info = []
    auto_end_index = -1  # ensure first loop starts at right enumerate index
    for off_start, auto_start, auto_end in tests:

        try:
            p = next(pv for t, pv in pgain if t > auto_end)
            i = next(pv for t, pv in itime if t > auto_end)
            d = next(pv for t, pv in dtime if t > auto_end)

            off_start_index = next(i for i, t in
                                   enumerate(temp_times, start=auto_end_index + 1) if t > off_start)
            auto_start_index = next(i for i, t in
                                    enumerate(temp_times, start=off_start_index + 1) if t > auto_start)
            auto_end_index = next(i for i, t in
                                  enumerate(temp_times, start=auto_start_index + 1) if t > auto_end)
        except StopIteration:
            continue

        off_to_auto = RampTest()  # off2auto
        off_to_auto.pgain = p
        off_to_auto.itime = i
        off_to_auto.dtime = d
        off_to_auto.start_index = off_start_index
        off_to_auto.end_index = auto_start_index
        off_to_auto.start_time = off_start
        off_to_auto.end_time = auto_start
        off_to_auto.test_name = "Off to Auto"

        auto_to_auto = RampTest()
        auto_to_auto.pgain = p
        auto_to_auto.itime = i
        auto_to_auto.dtime = d
        auto_to_auto.start_index = auto_start_index
        auto_to_auto.end_index = auto_end_index
        auto_to_auto.start_time = auto_start
        auto_to_auto.end_time = auto_end
        auto_to_auto.test_name = "Auto to Auto"

        full_test = RampTest()
        full_test.pgain = p
        full_test.itime = i
        full_test.dtime = d
        full_test.start_index = off_start_index
        full_test.end_index = auto_end_index
        full_test.start_time = off_start
        full_test.end_time = auto_end
        full_test.test_name = "Full Test"

        info.append((off_to_auto, auto_to_auto, full_test))

    return info


def main(filename: str) -> list:

    batch = open_batch(filename)
    tests = hardmode_auto2auto_tests(batch)
    info = find_auto2auto_settings(batch, tests)
    pickle_file = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\scripts\\test_stuff\\test_output.txt"
    pickle_info(info, pickle_file)
    pickle_info(OrderedDict(batch), manypickle)
    return info, batch


from os.path import exists as path_exists, split as path_split, splitext as path_splitext
from officelib.olutils import getFullLibraryPath


def full_scan_steps(steps_report: str) -> list:
    """
    @param steps_report: filename of steps report
    @type steps_report: str
    @return: list
    @rtype: list
    """
    _head, tail = path_split(steps_report)
    name, _ = path_splitext(tail)
    cache = '\\'.join((pickle_cache, name + '.pickle'))

    if path_exists(cache):
        tests = unpickle_info(cache)
    else:
        steps_report = getFullLibraryPath(steps_report)
        tests = find_full_tests(steps_report)
        pickle_info(tests, cache)

    return tests


def full_open_batch(data_report: str) -> BatchFile:
    """
    @param data_report: filename of data report
    @type data_report: str
    @return: BatchFile for report
    @rtype: BatchFile
    """
    _head, tail = path_split(data_report)
    name, _ = path_splitext(tail)
    cache = '\\'.join((pickle_cache, name + '.pickle'))

    if path_exists(cache):
        batch = unpickle_info(cache)
    else:
        data_report = getFullLibraryPath(data_report)
        batch = open_batch(data_report)
        pickle_info(batch, cache)

    return batch


def full_scan(data_report: str, steps_report: str) -> list:
    """
    @param data_report: filename of data report
    @type data_report: str
    @param steps_report: filename of steps report
    @type steps_report: str
    @return:
    @rtype:
    """

    batch = full_open_batch(data_report)
    tests = full_scan_steps(steps_report)

    all_tests = find_all_tests(tests, batch)
    all_tests = list(flatten(all_tests))

    process_tests(all_tests, batch)


def __profile_code():
    """
    @return: None
    @rtype: None

    Edit this function to do all profiling.
    """
    import cProfile
    from pstats import Stats
    profile_file = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\officelib\\pbslib\\test\\profile.txt"
    cProfile.run('full_scan(manyfile3, manyrecipesteps)', filename=profile_file)
    with open("C:\\Users\\Public\\Documents\\PBSSS\\Functional Testing\\tpid.txt", 'w') as f:
        stats = Stats(profile_file, stream=f)
        # stats.strip_dirs()
        stats.sort_stats('time')
        stats.print_stats('MSOffice')


if __name__ == "__main__":

    full_scan(manyfile3, manyrecipesteps)
    # __profile_code()
