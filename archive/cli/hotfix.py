"""

Created by: Nathan Starkweather
Created on: 10/03/2014
Created in: PyCharm Community Edition


Hotfixes for REPL sessions- import, %edit, use.
"""
from officelib.const import xlValue

__author__ = 'Nathan Starkweather'

import types

def hf_PIDRunner_chartbypid(r):
    from officelib.xllib.xlcom import FormatChart
    from collections import OrderedDict

    def fixed(self, ifpassed=False):
        """
        @param ifpassed: Only plot tests that passed
        @type ifpassed: Bool

        Group all tests with the same p,i,d settings into one chart. Ie,
        all setpoints for a given set of settings in one chart.
        """
        groups = OrderedDict()
        for t in self._results:

            if ifpassed and not t.passed:
                continue

            key = (t.p, t.i, t.d)
            if key not in groups:
                groups[key] = self._init_chart()
            t.chartplot(groups[key])

        # loop again and format + move charts to new sheets
        for key, chart in groups.items():
            p, i, d = key
            name = "P-%sI-%sD-%s" % (str(p), str(i), str(d))
            title = "PID Test: " + name
            try:
                FormatChart(chart, ChartTitle=title, xAxisTitle="Time (s)", yAxisTitle="RPM", Legend=False)
                chart.Location(1, name)
                chart.Axes(xlValue).HasMajorGridlines = True
            except:
                self._log_err("Error Formatting chart")

        self._chartmap = groups

    m = types.MethodType(fixed, r)
    r.chartbypid = m
