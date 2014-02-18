"""

Created by: Nathan Starkweather
Created on: 02/18/2014
Created in: PyCharm Community Edition

Script to analyze data for pressure based level sensor
"""

from officelib.pbslib import DataReport
from officelib.const import xlByRows, xlDown
from officelib.xllib.xlProxy import ChartSeries


def open_report(fpath):
    """
    @param fpath: filepath to data report
    @type fpath: str
    @return: DataReport
    @rtype: DataReport
    """
    return DataReport(fpath)


def find_chart_info(cells, name):
    """
    @param cells: xllib,typehint.typehint0x1x6.Range.Range
    @type cells: xllib.typehint.typehint0x1x6.Range.Range
    @param name: name in first row
    @type name: str
    @return: cell object
    @rtype: xllib.xlProxy.ChartSeries
    """
    result = cells.Find(What=name, SearchOrder=xlByRows)
    if not result:
        raise NameError("%s not found." % name)

    col, row = result.Column, result.Row + 1

    data = ChartSeries()
    data.x_column = col
    data.y_column = col + 1
    data.start_row = row
    data.end_row = result.End(xlDown).Row
    data.chart_name = "%s vs Time" % name
    data.series_name = name
    data.sheet_name = cells.Parent.Name

    return data


def make_chart(ws, series):
    """
    @param ws: worksheet
    @type ws: xllib.typehint.typehint0x1x6._Worksheet._Worksheet
    @param series: ChartSeries
    @type series: ChartSeries
    @return: chart
    @rtype: xllib.typehint.typehint0x1x6._Chart._Chart
    """

    from xllib.xlcom import CreateChart, FormatChart, CreateDataSeries

    chart = CreateChart(ws)
    FormatChart(chart, None, series.ChartTitle, "Time(min)", series.SeriesName, True)
    CreateDataSeries(chart, series.xSeriesRange, series.ySeriesRange)

    return chart


def make_elapsed_times(cells, param):
    """
    @param cells:
    @type cells: xllib.typehint.typehint0x1x6.Range.Range
    @param param:
    @type param:
    @return: None
    @rtype: None
    """

    target = cells.Find(param, SearchOrder=xlByRows)
    col, row = target.Column + 1, target.Row

    #: @type: xllib.typehint.typehint0x1x6._Worksheet._Worksheet
    ws = cells.Parent

    # ws.Columns(col).Insert()


def main(fpath):
    """
    @param fpath: str
    @type fpath: str
    @return: str
    @rtype: str
    """
    from xllib.xlcom import xlObjs, HiddenXl
    # report = open_report(fpath)
    # for param in report:
    #     print(param)
    xl, wb, ws, cells = xlObjs(fpath, visible=False)
    with HiddenXl(xl):

        make_elapsed_times(cells, "LevelPV(L)")
        make_elapsed_times(cells, "FilterOvenPV(C)")

        level_pv = find_chart_info(cells, "LevelPV(L)")
        exhaust_temp = find_chart_info(cells, "FilterOvenPV(C)")

        level_chart = make_chart(ws, level_pv)
        exhaust_chart = make_chart(ws, exhaust_temp)




if __name__ == '__main__':

    testfile = "C:\\Users\\PBS Biotech\\Documents\\Personal\\test files\\pressureval\\stability.csv"
    main(testfile)

