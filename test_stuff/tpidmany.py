"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""
from officelib.pbslib.proxies import BatchFile
from itertools import zip_longest
from officelib.pbslib.batchutil import ParseDateFormat, flatten
from weakref import ref as wref
from datetime import timedelta, datetime
from officelib.xllib.xladdress import cellStr, cellRangeStr
from os.path import exists as path_exists, split as path_split, splitext as path_splitext
from officelib.olutils import getFullLibraryPath


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


class ChartSeriesInfo():

    def __init__(self,
                 series_name='',
                 start_row=1,
                 end_row=2,
                 x_column=1,
                 y_column=2,
                 sheet_name='Sheet1',
                 chart_name=''):

        """
        @type series_name: str
        @type start_row: int > 0
        @type end_row: int > 0
        @type x_column: int > 0
        @type y_column: int > 0
        @type sheet_name: str
        @type chart_name: str
        """

        self.series_name = series_name
        self.start_row = start_row
        self.end_row = end_row
        self.x_column = x_column
        self.y_column = y_column
        self.sheet_name = sheet_name
        self.chart_name = chart_name

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
        """ If series name undefined, return formula
        for contents of top cell of Y column.

        Otherwise return series name.
        """
        if not self.series_name:
            name_row = max(self.start_row - 1, 1)  # avoid negatives or 0
            name = "=%s!" % self.sheet_name
            name += cellStr(name_row, self.y_column)
        else:
            name = self.series_name
        return name

    @property
    def ChartName(self):
        if not self.chart_name and self.series_name:
            return self.series_name
        return self.chart_name


def backup_settings() -> list:
    """
    @return: list of settings with constant
             ratio.
    """
    ps = [5 * i for i in range(1, 10)]
    settings = ((p, p / 10, 0) for p in ps)
    return list(settings)


def find_auto2auto_settings(batch: BatchFile, tests: list):
    """
    @param batch:
    @type batch:
    @param tests:
    @type tests:
    @return:
    @rtype:
    """
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

    return info


def pickle_info(info: object, filename: str):

    from pysrc.snippets import safe_pickle
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


def plot_tests(header, column_data, chart_series_list, header_row_offset):
    """
    @param header: iterable of tuples of header data to plot
    @type header: collections.Sequence[collections.Sequence]
    @param column_data: iterable of tuples of column data to plot
    @type column_data: collections.Sequence[collections.Sequence]
    @param chart_series_list: iterable of ChartSeriesInfo instances to plot
    @type chart_series_list: collections.Sequence[ChartSeriesInfo]
    @param header_row_offset: move the data down by this # of rows
    @type header_row_offset: int
    @return: None
    @rtype: None
    """

    data_row_offset = len(header) + header_row_offset
    rows = len(column_data)
    columns = len(column_data[0])

    data_area = cellRangeStr(
                            (1 + data_row_offset, 1),
                            (rows + data_row_offset, columns)
                             )
    header_area = cellRangeStr(
                            (1 + header_row_offset, 1),
                            (len(header) + header_row_offset, columns)
                            )

    from officelib.xllib.xlcom import xlObjs, CreateChart, \
                                        CreateDataSeries, FormatChart, VisibleXlGuard
    from officelib.const import xlXYScatterLinesNoMarkers, xlLocationAsNewSheet

    xl, wb, ws, cells = xlObjs(visible=False)

    with VisibleXlGuard(xl):
        ws_name = ws.Name

        cells.Range(header_area).Value = header
        cells.Range(data_area).Value = column_data

        chart_full = CreateChart(ws, xlXYScatterLinesNoMarkers)
        chart_a2a = CreateChart(ws, xlXYScatterLinesNoMarkers)
        chart_o2a = CreateChart(ws, xlXYScatterLinesNoMarkers)

        FormatChart(chart_full, None, "Full Test", "Time(min)", "TempPV(C)", True, True)
        FormatChart(chart_a2a, None, "Auto to Auto Test", "Time(min)", "TempPV(C)", True, True)
        FormatChart(chart_o2a, None, "Off to Auto Test", "Time(min)", "TempPV(C)", True, True)

        chart_map = {
            "Off to Auto": chart_o2a,
            "Auto to Auto": chart_a2a,
            "Full Test": chart_full
        }

        for info in chart_series_list:
            info.sheet_name = ws_name
            info.series_name = info.series_name % ws_name
            chart = chart_map[info.chart_name]
            CreateDataSeries(chart, info.XSeriesRange, info.YSeriesRange, info.SeriesName)

        for name, chart in chart_map.items():
            chart.Location(Where=xlLocationAsNewSheet, Name=name)


def process_tests(test_list, batch: BatchFile):
    """
    @param test_list: list of tests to process
    @type test_list: list[RampTest]
    @param batch: batch file corresponding to test list
    @type batch: BatchFile
    @return (xl, wb, ws, cells)
    @rtype (T, U, V, X)
    """

    temppv = batch['TempPV(C)']
    pv_times = temppv.Times.Datestrings
    pv_values = temppv.Values

    magic_name_formula1 = '=CONCATENATE("p",R[2]C[-1],"I",R[2]C,"d",R[2]C[1])'
    magic_name_formula2 = '=CONCATENATE(SUBSTITUTE(R[6]C[-1], " ", ""),R[1]C,R[1]C[1],R[2]C,R[2]C[1],R[3]C,R[3]C[1])'

    columns_per_test = 5  # including blank spacer
    header_row_offset = 0
    data_row_offset = header_row_offset + 10

    # Using a bunch of lists for rows is ugly, but easiest way to
    # avoid having to transpose the whole header later.
    # Just define header to be a list of all of the rows.
    # this also makes it a bit clearer (imo) what's going on in the loop
    # instead of multiassigning, assign header separately.
    # otherwise, Pycharm type hinting gets confused.

    column_data = []
    row1 = []
    row2 = []
    row3 = []
    row4 = []
    row5 = []
    row6 = []
    row7 = []
    row8 = []
    row9 = []
    row10 = []

    series_list = []
    for n, test in enumerate(test_list):

        start_index = test.start_index
        end_index = test.end_index
        times = pv_times[start_index:end_index]
        values = pv_values[start_index:end_index]

        column = n * columns_per_test + 1
        ref_cell = (data_row_offset + 1, column)
        rows = len(times)
        elapsed_times = _make_elapsed(ref_cell, column + 1, rows)

        series_info = ChartSeriesInfo()
        series_info.series_name = "=%s!" + cellStr(1, column + 1)
        series_info.start_row = data_row_offset + 1
        series_info.end_row = data_row_offset + rows
        series_info.x_column = column + 1
        series_info.y_column = column + 2
        series_info.chart_name = test.test_name
        series_list.append(series_info)

        column_data.extend([times, elapsed_times, values, (None,), (None,)])  # Need iterable placeholders for zip_longest

        row1.extend(("Name", magic_name_formula2, None, None, None))
        row2.extend(("Settings:", "P", "=R[7]C[-2]", None, None))
        row3.extend((None, "I", "=R[6]C[-1]", None, None))
        row4.extend((None, "D", "=R[5]C", None, None))
        row5.extend((None, "AutoMax%", "50", None, None))
        row6.extend((None, "SP", "39", None, None))
        row7.extend((test.test_name, magic_name_formula1, None, None, None))
        row8.extend(('Pgain', 'Itime', 'Dtime', None, None))
        row9.extend((test.pgain, test.itime, test.dtime, None, None))
        row10.extend(("Test Time", "Elapsed Time", "TempPV(C)", None, None))

    header = [
            row1,
            row2,
            row3,
            row4,
            row5,
            row6,
            row7,
            row8,
            row9,
            row10
            ]

    column_data = list(zip_longest(*column_data))

    plot_tests(header,
                column_data,
                series_list,
                header_row_offset)


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
    pickle_info(batch, manypickle)
    return info, batch


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
