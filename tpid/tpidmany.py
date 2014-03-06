"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition

Functions to analyze long tpid recipes containing many
individual tpid tests.

Public functions:

full_scan(data_report_filename, steps_report_filename, report_time_diff) ->
            Analyze everything and plot in  excel. This function binds together everything
            from below.


open_batch(filename) -> DataReport instance derived from the filename

pickle_info(obj, filename) -> save the object to filename

unpickle_info(filename) -> unpickle the object


full_open_data_report(filename) -> fully open the batch report, either freshly or from pickled info

full_scan_steps(filename) -> return list of (off_to_auto_start, auto_to_auto_start, end) datetimes from report

map_batch_steps(steps, data) -> map tests from full_scan_steps, data from full_open_data_report into
                                list of RampTest instances corresponding to steps from full_scan_steps.
                                Steps are returned as (off_to_auto, auto_to_auto, full_test).

process_tests(test_list, data) -> process all tests in the list corresponding to the data report and plot in
                                excel. Be sure to flatten the list from map_batch_steps before passing anything
                                in.

"""
from itertools import zip_longest, chain
from datetime import timedelta, datetime
from os.path import exists as path_exists, split as path_split, splitext as path_splitext

from pbslib.recipemaker.tpid_recipes import cool_start as _get_recipe_start
from pbslib.batchreport import DataReport, ParseDateFormat, quick_strptime
from officelib.xllib.xladdress import cellStr, cellRangeStr
from officelib.olutils import getFullLibraryPath


def flatten(iterable):
    return chain.from_iterable(iterable)


manyfile = "C:\\Users\\PBS Biotech\\Downloads\\2014020613364723.csv"
manyfile2 = "C:\\Users\\PBS Biotech\\Downloads\\overnight2.csv"
manypickle = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\scripts\\test_stuff\\manyfile.txt"
manyfile3 = "C:\\Users\\PBS Biotech\\Downloads\\overweekend.csv"
manyrecipesteps = "C:\\Users\\PBS Biotech\\Downloads\\weekendsteps.csv"
pickle_cache = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\scripts\\test_stuff\\pickle_cache"


class RampTestResult():
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
    @param end_index: PYTHON end index- same as python slice ie last one you don't want
    @type end_index: int
    @param x_data: x_data
    @type x_data: collections.Sequence[datetime.datetime]
    @param y_data: y_data
    @type y_data: collections.Sequence[int | float]
    """
    def __init__(self,
                pgain=0,
                itime=0,
                dtime=0,
                start_time=None,
                end_time=None,
                start_index=0,
                end_index=0,
                test_name="Temp PID Test",
                x_data=None,
                y_data=None):
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
        @param end_index: PYTHON end index- same as python slice ie last one you don't want
        @type end_index: int
        @param x_data: x_data
        @type x_data: collections.Sequence[datetime.datetime]
        @param y_data: y_data
        @type y_data: collections.Sequence[int | float]
        """
        self.pgain = pgain
        self.itime = itime
        self.dtime = dtime
        self.start_time = start_time
        self.end_time = end_time
        self.start_index = start_index
        self.end_index = end_index
        self.test_name = test_name
        self.x_data = x_data
        self.y_data = y_data

    def __repr__(self) -> str:
        """
        @return: human readable representation. For debugging/interactive console use.
        @rtype: str
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


class ChartSeries():
    """
    @type series_name: str
    @type start_row: int
    @type end_row: int
    @type x_column: int
    @type y_column: int
    @type sheet_name: str
    @type chart_name: str
    """

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
        @type start_row: int
        @type end_row: int
        @type x_column: int
        @type y_column: int
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
        series_name = self.series_name
        if not series_name:
            name_row = max(self.start_row - 1, 1)  # avoid negatives or 0
            name = "=%s!" % self.sheet_name
            name += cellStr(name_row, self.y_column)
        else:
            name = series_name
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


def find_auto2auto_settings(report, tests):
    """
    @param report: DataReport
    @type report: DataReport
    @param tests: list[(int, int, datetime, datetime)]
    @type tests: list[(int, int, datetime, datetime)]
    @return: list of ramp tests
    @rtype: list[RampTestResult]
    """
    pgain = report["TempHeatDutyControl.PGain(min)"]
    itime = report["TempHeatDutyControl.ITime(min)"]
    dtime = report["TempHeatDutyControl.DTime(min)"]

    info = []
    for start_index, end_index, start, end in tests:
        p = next(pv for t, pv in pgain if t > start)
        i = next(pv for t, pv in itime if t > start)
        d = next(pv for t, pv in dtime if t > start)

        test = RampTestResult(p, i, d, start, end, start_index, end_index)

        info.append(test)

    return info


def hardmode_auto2auto_tests(report, settle_seconds=1200):
    """
    @param report: report
    @type report: DataReport
    @param settle_seconds: seconds for settle time steps
    @type settle_seconds: int
    @return: list[(int, int, datetime, datetime)]
    @rtype: list[(int, int, datetime, datetime)]

    Get the auto-to-auto tests out of a batch file
    that forgot to record the TempSP. Start point, set-point
    must be 37, 39 respectively.

    If you need to use this, something went wrong,
    and you should probably fix that instead of
    relying on this.
    """

    temppv = report['TempPV(C)']
    data = iter(temppv)
    settle_time = timedelta(seconds=settle_seconds)

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
        # find the timestamp after waiting the second settle time.
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


__start_steps = len(_get_recipe_start())


def extract_test_steps(steps,
                            skip_steps=__start_steps,
                            off_start_step='Set "TempModeUser" to Auto',
                            auto_start_step='Set "TempSP(C)" to 39',
                            end_step='Set "TempModeUser" to Off'):
    """
    Internal scanning function unique to a certain type of recipe
    steps test. I'm not sure how to distinguish between them
    in a programmatically friendly way for use outside this module,
    so for now just swap them manually when necessary.

    A steps report has the column format of
    Step_Type, TimeStamp, StepCommand

    Only timestamp and stepcommand are needed.

    @param steps: list of recipe steps
    @type steps: list[(str, str, str)]
    @return: list of tests start and stop time
    @rtype: list[(str, str, str)]

    """
    tests = []
    iter_steps = iter(steps)

    # bump iterator forward until first test start.
    next(i for i in range(skip_steps))

    while True:
        try:
            off_start = next(time for _, time, step in iter_steps if step == off_start_step)
            auto_start = next(time for _, time, step in iter_steps if step == auto_start_step)
            auto_end = next(time for _, time, step in iter_steps if step == end_step)
        except StopIteration:
            break

        tests.append((off_start, auto_start, auto_end))

    return tests


def extract_raw_steps(steps_filename):
    """
    @param steps_filename: steps file to extract steps from
    @type steps_filename: str
    @return: list of steps as strings
    @rtype: list[(str, str, str)]
    """
    with open(steps_filename, 'r') as f:
        f.readline()
        steps = [line.strip().split(',') for line in f.readlines()]
    return steps


def parse_test_dates(tests, time_offset=0):
    """
    @param tests: list of
    @type tests: list[(str, str, str)]
    @param time_offset: Increment all times by this amount of minutes.
    @type time_offset: None | int
    @return: list of Off-to-auto start, auto-to-auto start
    @rtype: list[(datetime, datetime, datetime)]

    Note that this scanning function is unique to the recipe I've been using
    so far (due to extract_test_steps()). Changes in recipe == need to write
    a new function.
    """

    # The recipe steps report gives inaccurate timestamps, sometimes,
    # so we need to fix it by adding one hour.
    parse_fmt = ParseDateFormat
    strptime = quick_strptime
    parsed = []

    # offset = timedelta(minutes=time_offset or 0)
    # for off_start, auto_start, auto_end in tests:
    #     fmt = parse_fmt(off_start)
    #     off_start = strptime(off_start, fmt) + offset
    #     auto_start = strptime(auto_start, fmt) + offset
    #     auto_end = strptime(auto_end, fmt) + offset
    #     parsed.append((off_start, auto_start, auto_end))

    offset = timedelta(minutes=time_offset or 0)
    fmt = parse_fmt(tests[0][0])  # initial guess
    for test in tests:
        datetimes = (strptime(time, parse_fmt(time, fmt)) + offset for time in test)
        parsed.append(tuple(datetimes))

    return parsed


def unpickle_info(filename):
    """
    @param filename: filename
    @type filename: str
    @return: unpickled info
    @rtype: T
    """
    from pickle import load as pickle_load
    with open(filename, 'rb') as f:
        info = pickle_load(f)

    return info


def pickle_info(info, filename):
    """
    @param info: object
    @type info: T
    @param filename: filename
    @type filename: str
    @return: None
    @rtype: None
    """

    from pysrc.snippets import safe_pickle
    safe_pickle(info, filename)


def make_elapsed_times(ref_cell, target_column, rows):
    """
    @param ref_cell: reference cell to use for elapsed time column
    @type ref_cell: (int, int)
    @param target_column: start cell for elapsed time column
    @type target_column: int
    @param rows: number of rows
    @type rows: int
    @return: list of formulas in r1c1 style (autoconverted by excel)
    @rtype: list[str]

    Helper for process_tests.
    Ref cell as tuple instead of just "knowing" that
    columns are next to each other, in case function
    needs to be extended.
    """
    ref_row, ref_col = ref_cell
    offset = ref_col - target_column  # offset should be negative if col > ref_col
    formula = "=(RC[{0}] - R{1}C{2}) * 1440".format(offset, ref_row, ref_col)

    return [formula for _ in range(rows)]


def __prepare_charts_all_tests(ws):
    """
    @param ws:
    @type ws:
    @return:
    @rtype:
    """

    from officelib.xllib.xlcom import CreateChart, FormatChart, FormatAxesScale
    from officelib.const import xlXYScatterLinesNoMarkers

    chart_full = CreateChart(ws, xlXYScatterLinesNoMarkers)
    chart_a2a = CreateChart(ws, xlXYScatterLinesNoMarkers)
    chart_o2a = CreateChart(ws, xlXYScatterLinesNoMarkers)
    FormatChart(chart_full, None, "Full Test", "Time(min)", "TempPV(C)", True, True)
    FormatChart(chart_a2a, None, "Auto to Auto Test", "Time(min)", "TempPV(C)", True, True)
    FormatChart(chart_o2a, None, "Off to Auto Test", "Time(min)", "TempPV(C)", True, True)
    FormatAxesScale(chart_full, 0, None, 36, 40)
    FormatAxesScale(chart_a2a, 0, None, 38.8, 39.2)
    FormatAxesScale(chart_o2a, 0, None, 36.8, 37.2)
    return chart_a2a, chart_full, chart_o2a


def plot_tests(header, column_data, chart_series_list, header_row_offset):
    """
    @param header: iterable of tuples of header data to plot
    @type header: collections.Sequence[collections.Sequence]
    @param column_data: iterable of tuples of column data to plot
    @type column_data: collections.Sequence[collections.Sequence]
    @param chart_series_list: iterable of ChartSeries instances to plot
    @type chart_series_list: collections.Sequence[ChartSeries]
    @param header_row_offset: move the data down by this # of rows
    @type header_row_offset: int
    @return: None
    @rtype: None

    Plot all the tests. Header and column data should correspond.
    Function isn't private but is probably very hard to use
    outside of being called automatically by other module functions.
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

    # Because importing xllib requires importing win32com, and
    # win32com can be very slow to initialize, wait until here to
    # do the import, so that any errors thrown will abort analysis
    # before getting to this point.

    from officelib.xllib.xlcom import xlObjs, CreateDataSeries, HiddenXl
    from officelib.const import xlLocationAsNewSheet

    xl, wb, ws, cells = xlObjs(visible=False)

    with HiddenXl(xl):
        ws_name = ws.Name

        cells.Range(header_area).Value = header
        cells.Range(data_area).Value = column_data

        chart_a2a, chart_full, chart_o2a = __prepare_charts_all_tests(ws)

        chart_map = {
            "Off to Auto": chart_o2a,
            "Auto to Auto": chart_a2a,
            "Full Test": chart_full
        }

        for series in chart_series_list:
            chart = chart_map[series.chart_name]
            series.sheet_name = ws_name
            series.series_name = series.series_name % ws_name
            CreateDataSeries(chart, series.XSeriesRange, series.YSeriesRange, series.SeriesName)

        for name, chart in chart_map.items():
            chart.Location(Where=xlLocationAsNewSheet, Name=name)

    return wb


def _make_series_info(column, start_row, rows, ramp_test):
    """
    @param column: column
    @type column: int
    @param start_row: start_row
    @type start_row: int
    @param rows: number of rows
    @type rows: int
    @param ramp_test: the ramp test
    @type ramp_test: RampTestResult
    @return: series info
    @rtype: ChartSeries

    Helper function for process_tests to make chart series info.
    """
    series_info = ChartSeries()
    series_info.series_name = "=%s!" + cellStr(1, column + 1)
    series_info.start_row = start_row
    series_info.end_row = start_row + rows
    series_info.x_column = column + 1
    series_info.y_column = column + 2
    series_info.chart_name = ramp_test.test_name
    return series_info


def _extend_tests_header(header, ramp_test):
    """
    @param header: the header
    @type header: collections.Sequence[list[str]]
    @param ramp_test: RampTestResult
    @type ramp_test: RampTestResult
    @return: None
    @rtype: None

    Internal helper for process_tests. Update the header by
    extending each of the rows.

    Use formulas instead of values to enter some of the text.
    This allows default values determined by this module to be
    used in one location, and the rest of the locations to refer
    to those cell entries. This way, user can simply update a single
    cell, and the rest of the entries will be re-calculated automatically.
    """

    name_formula1 = '=CONCATENATE(SUBSTITUTE(R[6]C[-1], " ", ""),R[1]C,R[1]C[1],R[2]C,R[2]C[1],R[3]C,R[3]C[1])'
    name_formula2 = '=CONCATENATE("p",R[2]C[-1],"I",R[2]C,"d",R[2]C[1])'
    p_formula = "=R[7]C[-2]"
    i_formula = "=R[6]C[-1]"
    d_formula = "=R[5]C"

    header[0].extend(("Name", name_formula1, None, None, None))
    header[1].extend(("Settings:", "P", p_formula, None, None))
    header[2].extend((None, "I", i_formula, None, None))
    header[3].extend((None, "D", d_formula, None, None))
    header[4].extend((None, "AutoMax%", "50", None, None))
    header[5].extend((None, "SP", "39", None, None))
    header[6].extend((ramp_test.test_name, name_formula2, None, None, None))
    header[7].extend(('Pgain', 'Itime', 'Dtime', None, None))
    header[8].extend((ramp_test.pgain, ramp_test.itime, ramp_test.dtime, None, None))
    header[9].extend(("Test Time", "Elapsed Time", "TempPV(C)", None, None))


def process_tests(test_list, data):
    """
    @param test_list: list of tests to process
    @type test_list: list[RampTestResult]
    @param data: data file corresponding to test list
    @type data: DataReport
    @return (xl, wb, ws, cells)
    @rtype (T, U, V, X)
    """
    temppv = data['TempPV(C)']
    pv_times = temppv.Times.Datestrings
    pv_values = temppv.Values

    columns_per_test = 5  # including blank spacer
    header_row_offset = 0
    data_row_offset = header_row_offset + 10

    # Using a bunch of lists for rows is ugly, but easiest way to
    # avoid having to transpose the whole header later.
    # Just define header to be a list of lists of rows
    # this also makes it a bit clearer (imo) what's going on in the loop

    column_data = []
    header = [[] for _ in range(10)]  # 10 empty lists -> 10 rows
    series_list = []
    for n, ramp_test in enumerate(test_list):
        start_index = ramp_test.start_index
        end_index = ramp_test.end_index
        times = pv_times[start_index:end_index]
        values = pv_values[start_index:end_index]
        column = n * columns_per_test + 1
        ref_cell = (data_row_offset + 1, column)
        rows = end_index - start_index

        # assert rows == len(times) == len(values)  # DEBUG

        elapsed_times = make_elapsed_times(ref_cell, column + 1, rows)
        series_info = _make_series_info(column, data_row_offset + 1, rows, ramp_test)
        series_list.append(series_info)
        column_data.extend((times, elapsed_times, values, (None,), (None,)))  # Need iterable None for zip_longest
        _extend_tests_header(header, ramp_test)

    # Transpose data from column to row order
    column_data = list(zip_longest(*column_data))
    return plot_tests(header, column_data, series_list, header_row_offset)


def map_batch_steps(steps, data):
    """
    @param steps: list of steps (start, end1, start2, end2) datetimes
    @type steps: list[(datetime, datetime, datetime)]
    @param data: data file corresponding to steps
    @param data: DataReport
    @return: list of steps with indicies.
    @rtype: list[(RampTestResult, RampTestResult, RampTestResult)]

    This process is rather different than the Auto2Auto settings finder,
    so needs its own implementation despite identical code in some places.
    """
    pgain = data["TempHeatDutyControl.PGain(min)"]
    itime = data["TempHeatDutyControl.ITime(min)"]
    dtime = data["TempHeatDutyControl.DTime(min)"]
    pvs = data['TempPV(C)'].Values
    times = data['TempPV(C)'].Times
    temp_times = iter(times)
    info = []
    auto_end_index = -1  # ensure first loop starts at right enumerate index
    for off_start, auto_start, auto_end in steps:

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

        off_to_auto = RampTestResult()
        off_to_auto.pgain = p
        off_to_auto.itime = i
        off_to_auto.dtime = d
        off_to_auto.start_index = off_start_index
        off_to_auto.end_index = auto_start_index
        off_to_auto.x_data = times[off_start_index:auto_start_index]
        off_to_auto.y_data = pvs[off_start_index:auto_start_index]
        off_to_auto.start_time = off_start
        off_to_auto.end_time = auto_start
        off_to_auto.test_name = "Off to Auto"

        auto_to_auto = RampTestResult()
        auto_to_auto.pgain = p
        auto_to_auto.itime = i
        auto_to_auto.dtime = d
        auto_to_auto.start_index = auto_start_index
        auto_to_auto.end_index = auto_end_index
        auto_to_auto.x_data = times[auto_start_index:auto_end_index]
        auto_to_auto.y_data = pvs[auto_start_index:auto_end_index]
        auto_to_auto.start_time = auto_start
        auto_to_auto.end_time = auto_end
        auto_to_auto.test_name = "Auto to Auto"

        full_test = RampTestResult()
        full_test.pgain = p
        full_test.itime = i
        full_test.dtime = d
        full_test.start_index = off_start_index
        full_test.end_index = auto_end_index
        full_test.x_data = times[off_start_index:auto_end_index]
        full_test.y_data = pvs[off_start_index:auto_end_index]
        full_test.start_time = off_start
        full_test.end_time = auto_end
        full_test.test_name = "Full Test"

        info.append((off_to_auto, auto_to_auto, full_test))

    return info


def old_main(filename: str) -> list:

    batch = DataReport(filename)
    tests = hardmode_auto2auto_tests(batch)
    info = find_auto2auto_settings(batch, tests)
    pickle_file = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\scripts\\test_stuff\\test_output.txt"
    pickle_info(info, pickle_file)
    pickle_info(batch, manypickle)
    return info, batch


def full_scan_steps(steps_report, time_offset=None):
    """
    @param steps_report: filename of steps report
    @type steps_report: str
    @param time_offset: sometimes recipe steps bugs out. Increment all times by this amount of minutes.
    @type time_offset: None | int
    @return: list
    @rtype: list[(datetime, datetime, datetime)]
    """

    cache = _get_cache_name(steps_report)

    if path_exists(cache) and _cache_is_recent(steps_report, cache):
        tests = unpickle_info(cache)
    else:
        steps_report = getFullLibraryPath(steps_report)
        steps = extract_raw_steps(steps_report)
        tests = extract_test_steps(steps)
        tests = parse_test_dates(tests, time_offset)
        pickle_info(tests, cache)

    return tests


def _get_cache_name(filename):
    """
    @param filename: filename to get cache name for
    @type filename: str
    @return: the name of the corresponding pickle cache
    @rtype: str
    """

    _, tail = path_split(filename)
    name, _ = path_splitext(tail)
    cache = '\\'.join((pickle_cache, name + '.pickle'))
    return cache


def full_open_data_report(csv_report):
    """
    Open the data report and create a DataReport
    instance from the file. The result is also cached
    in a .pickle file for intra-runtime persistance.

    Attempt first to see if a corresponding .pickle cache file
    exists for the same report upon being called, and if the
    cache is considered 'recent'.

    To be recent, the .pickle file must have been modified
    more recently than both the script and the corresponding
    .csv data report.

    This function will probably bug out if filenames passed
    are identical, even if paths weren't.

    @param csv_report: csv_report of data report
    @type csv_report: str
    @return: DataReport for report
    @rtype: DataReport
    """

    cache = _get_cache_name(csv_report)

    if path_exists(cache) and _cache_is_recent(csv_report, cache):
        batch = unpickle_info(cache)
    else:
        csv_report = getFullLibraryPath(csv_report)
        batch = DataReport(csv_report)
        pickle_info(batch, cache)

    return batch


def full_scan(data_report: str, steps_report: str, steps_time_offset=None):
    """
    @param data_report: filename of data report
    @type data_report: str
    @param steps_report: filename of steps report
    @type steps_report: str
    @param steps_time_offset: minutes to add to steps report times (to fix RIO bug, not our fault)
    @type steps_time_offset: None | int
    @return: workbook
    @rtype: officelib.xllib.typehint.th0x1x6._Workbook._Workbook
    """

    batch = full_open_data_report(data_report)
    tests = full_scan_steps(steps_report, steps_time_offset)
    all_tests = map_batch_steps(tests, batch)
    all_tests = list(flatten(all_tests))

    return process_tests(all_tests, batch)


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


from os import stat as os_stat

__last_save = os_stat(__file__).st_mtime


def _cache_is_recent(report_file, cache_file, script_modified=__last_save):
    """
    @param report_file: the file to check cache for
    @type report_file: str
    @param cache_file: the cached data file corresponding to the report file
    @type cache_file: str
    @param script_modified: time after which cache is considered outdated
    @type script_modified: float
    @return: bool
    @rtype: bool
    """

    report_modified = os_stat(report_file).st_mtime
    cache_modified = os_stat(cache_file).st_mtime

    return cache_modified > report_modified and cache_modified > script_modified


def tpid_eval_steps_scan(steps_file):

    steps = extract_raw_steps(steps_file)
    tests = [quick_strptime(date, ParseDateFormat(date))
             for _, date, step in steps if 'Set "TempSP(C)"' in step]
    # steps_iter = iter(steps)

    return tests


if __name__ == "__main__":

    # __profile_code()

    # data4 = "C:\\users\\pbs biotech\\downloads\\ovntpids4data (1).csv"
# steps4 = "C:\\users\\pbs biotech\\downloads\\ovntpids4steps (1).csv"
# wb = full_scan(data4, steps4)
# xl = wb.Parent
# xl.Visible = True

    steps = "C:\\Users\\PBS Biotech\\Downloads\\p40i6evalsteps.csv"
    tests = tpid_eval_steps_scan(steps)

    for i, t in enumerate(tests):
        try:
            print("Start: ", t)
            print("End: ", tests[i + 1], '\n')
        except IndexError:
            pass


