"""

Created by: Nathan Starkweather
Created on: 02/25/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

steps_report1_expected_lines = [
    ['Step Type', 'Date Time', 'Step Name'],
    ['Wait', '2/7/2014 5:08:29 PM', 'Wait 5 seconds'],
    ['Set', '2/7/2014 5:08:29 PM', 'Set "TempModeUser" to Off'],
    ['Wait Until', '2/7/2014 5:08:34 PM', 'Wait until "TempPV(C)" <= 28'],
    ['Set', '2/7/2014 8:32:13 PM', 'Set "TempHeatDutyControl.PGain(min)" to 5'],
    ['Set', '2/7/2014 8:32:13 PM', 'Set "TempHeatDutyControl.ITime(min)" to 0.5'],
    ['Set', '2/7/2014 8:32:13 PM', 'Set "TempHeatDutyControl.DTime(min)" to 0'],
    ['Set', '2/7/2014 8:32:13 PM', 'Set "TempSP(C)" to 37'],
    ['Wait', '2/7/2014 8:32:13 PM', 'Wait 5 seconds'],
    ['Set', '2/7/2014 8:32:18 PM', 'Set "TempModeUser" to Auto'],
    ['Wait Until', '2/7/2014 8:32:18 PM', 'Wait until "TempPV(C)" >= 37'],
    ['Wait', '2/7/2014 9:05:19 PM', 'Wait 3600 seconds'],
    ['Set', '2/7/2014 10:05:19 PM', 'Set "TempSP(C)" to 39'],
    ['Wait', '2/7/2014 10:05:19 PM', 'Wait 5 seconds'],
    ['Wait Until', '2/7/2014 10:05:24 PM', 'Wait until "TempPV(C)" >= 39'],
    ['Wait', '2/7/2014 10:18:34 PM', 'Wait 3600 seconds'],
    ['Wait Until', '2/7/2014 11:18:35 PM', 'Wait until "TempPV(C)" <= 28'],
    ['Set', '2/7/2014 11:18:35 PM', 'Set "TempModeUser" to Off'],
    ['Set', '2/8/2014 4:39:48 AM', 'Set "TempHeatDutyControl.PGain(min)" to 10'],
    ['Set', '2/8/2014 4:39:48 AM', 'Set "TempHeatDutyControl.ITime(min)" to 1.0'],
    ['Set', '2/8/2014 4:39:48 AM', 'Set "TempHeatDutyControl.DTime(min)" to 0'],
    ['Set', '2/8/2014 4:39:48 AM', 'Set "TempSP(C)" to 37'],
    ['Wait', '2/8/2014 4:39:48 AM', 'Wait 5 seconds'],
    ['Set', '2/8/2014 4:39:54 AM', 'Set "TempModeUser" to Auto'],
    ['Wait Until', '2/8/2014 4:39:54 AM', 'Wait until "TempPV(C)" >= 37'],
    ['Wait', '2/8/2014 5:12:39 AM', 'Wait 3600 seconds'],
    ['Set', '2/8/2014 6:12:40 AM', 'Set "TempSP(C)" to 39'],
    ['Wait', '2/8/2014 6:12:40 AM', 'Wait 5 seconds'],
    ['Wait Until', '2/8/2014 6:12:45 AM', 'Wait until "TempPV(C)" >= 39'],
    ['Wait', '2/8/2014 6:24:44 AM', 'Wait 3600 seconds'],
    ['Set', '2/8/2014 7:24:45 AM', 'Set "TempModeUser" to Off'],
    ['Wait Until', '2/8/2014 7:24:45 AM', 'Wait until "TempPV(C)" <= 28'],
    ['Set', '2/8/2014 12:59:42 PM', 'Set "TempHeatDutyControl.PGain(min)" to 15'],
    ['Set', '2/8/2014 12:59:42 PM', 'Set "TempHeatDutyControl.ITime(min)" to 1.5'],
    ['Set', '2/8/2014 12:59:42 PM', 'Set "TempHeatDutyControl.DTime(min)" to 0'],
    ['Set', '2/8/2014 12:59:42 PM', 'Set "TempSP(C)" to 37'],
    ['Wait', '2/8/2014 12:59:42 PM', 'Wait 5 seconds'],
    ['Set', '2/8/2014 12:59:47 PM', 'Set "TempModeUser" to Auto'],
    ['Wait Until', '2/8/2014 12:59:47 PM', 'Wait until "TempPV(C)" >= 37'],
    ['Wait', '2/8/2014 1:32:14 PM', 'Wait 3600 seconds'],
    ['Set', '2/8/2014 2:32:15 PM', 'Set "TempSP(C)" to 39'],
    ['Wait', '2/8/2014 2:32:15 PM', 'Wait 5 seconds'],
    ['Wait Until', '2/8/2014 2:32:20 PM', 'Wait until "TempPV(C)" >= 39'],
    ['Wait', '2/8/2014 2:43:25 PM', 'Wait 3600 seconds'],
    ['Wait Until', '2/8/2014 3:43:26 PM', 'Wait until "TempPV(C)" <= 28'],
    ['Set', '2/8/2014 3:43:26 PM', 'Set "TempModeUser" to Off'],
    ['Set', '2/8/2014 9:41:12 PM', 'Set "TempHeatDutyControl.PGain(min)" to 20'],
    ['Set', '2/8/2014 9:41:12 PM', 'Set "TempHeatDutyControl.ITime(min)" to 2.0'],
    ['Set', '2/8/2014 9:41:12 PM', 'Set "TempHeatDutyControl.DTime(min)" to 0'],
    ['Set', '2/8/2014 9:41:12 PM', 'Set "TempSP(C)" to 37'],
    ['Wait', '2/8/2014 9:41:12 PM', 'Wait 5 seconds'],
    ['Set', '2/8/2014 9:41:17 PM', 'Set "TempModeUser" to Auto'],
    ['Wait Until', '2/8/2014 9:41:17 PM', 'Wait until "TempPV(C)" >= 37'],
    ['Wait', '2/8/2014 10:14:08 PM', 'Wait 3600 seconds'],
    ['Set', '2/8/2014 11:14:09 PM', 'Set "TempSP(C)" to 39'],
    ['Wait', '2/8/2014 11:14:09 PM', 'Wait 5 seconds'],
    ['Wait Until', '2/8/2014 11:14:14 PM', 'Wait until "TempPV(C)" >= 39'],
    ['Wait', '2/8/2014 11:24:45 PM', 'Wait 3600 seconds'],
    ['Set', '2/9/2014 12:24:45 AM', 'Set "TempModeUser" to Off'],
    ['Wait Until', '2/9/2014 12:24:45 AM', 'Wait until "TempPV(C)" <= 28'],
    ['Set', '2/9/2014 6:07:11 AM', 'Set "TempHeatDutyControl.PGain(min)" to 25'],
    ['Set', '2/9/2014 6:07:11 AM', 'Set "TempHeatDutyControl.ITime(min)" to 2.5'],
    ['Set', '2/9/2014 6:07:11 AM', 'Set "TempHeatDutyControl.DTime(min)" to 0'],
    ['Set', '2/9/2014 6:07:11 AM', 'Set "TempSP(C)" to 37'],
    ['Wait', '2/9/2014 6:07:11 AM', 'Wait 5 seconds'],
    ['Set', '2/9/2014 6:07:16 AM', 'Set "TempModeUser" to Auto'],
    ['Wait Until', '2/9/2014 6:07:16 AM', 'Wait until "TempPV(C)" >= 37'],
    ['Wait', '2/9/2014 6:40:46 AM', 'Wait 3600 seconds'],
    ['Set', '2/9/2014 7:40:46 AM', 'Set "TempSP(C)" to 39'],
    ['Wait', '2/9/2014 7:40:46 AM', 'Wait 5 seconds'],
    ['Wait Until', '2/9/2014 7:40:52 AM', 'Wait until "TempPV(C)" >= 39'],
    ['Wait', '2/9/2014 7:51:09 AM', 'Wait 3600 seconds'],
    ['Wait Until', '2/9/2014 8:51:09 AM', 'Wait until "TempPV(C)" <= 28'],
    ['Set', '2/9/2014 8:51:09 AM', 'Set "TempModeUser" to Off'],
    ['Set', '2/9/2014 3:16:01 PM', 'Set "TempHeatDutyControl.PGain(min)" to 30'],
    ['Set', '2/9/2014 3:16:01 PM', 'Set "TempHeatDutyControl.ITime(min)" to 3.0'],
    ['Set', '2/9/2014 3:16:01 PM', 'Set "TempHeatDutyControl.DTime(min)" to 0'],
    ['Set', '2/9/2014 3:16:01 PM', 'Set "TempSP(C)" to 37'],
    ['Wait', '2/9/2014 3:16:01 PM', 'Wait 5 seconds'],
    ['Set', '2/9/2014 3:16:07 PM', 'Set "TempModeUser" to Auto'],
    ['Wait Until', '2/9/2014 3:16:07 PM', 'Wait until "TempPV(C)" >= 37'],
    ['Wait', '2/9/2014 3:51:06 PM', 'Wait 3600 seconds'],
    ['Set', '2/9/2014 4:51:06 PM', 'Set "TempSP(C)" to 39'],
    ['Wait', '2/9/2014 4:51:06 PM', 'Wait 5 seconds'],
    ['Wait Until', '2/9/2014 4:51:12 PM', 'Wait until "TempPV(C)" >= 39'],
    ['Wait', '2/9/2014 5:02:04 PM', 'Wait 3600 seconds'],
    ['Set', '2/9/2014 6:02:05 PM', 'Set "TempModeUser" to Off'],
    ['Wait Until', '2/9/2014 6:02:05 PM', 'Wait until "TempPV(C)" <= 28'],
    ['Set', '2/10/2014 12:15:20 AM', 'Set "TempHeatDutyControl.PGain(min)" to 35'],
    ['Set', '2/10/2014 12:15:20 AM', 'Set "TempHeatDutyControl.ITime(min)" to 3.5'],
    ['Set', '2/10/2014 12:15:21 AM', 'Set "TempHeatDutyControl.DTime(min)" to 0'],
    ['Set', '2/10/2014 12:15:21 AM', 'Set "TempSP(C)" to 37'],
    ['Wait', '2/10/2014 12:15:21 AM', 'Wait 5 seconds'],
    ['Set', '2/10/2014 12:15:26 AM', 'Set "TempModeUser" to Auto'],
    ['Wait Until', '2/10/2014 12:15:26 AM', 'Wait until "TempPV(C)" >= 37'],
    ['Wait', '2/10/2014 1:24:54 AM', 'Wait 3600 seconds'],
    ['Set', '2/10/2014 2:24:54 AM', 'Set "TempSP(C)" to 39'],
    ['Wait', '2/10/2014 2:24:54 AM', 'Wait 5 seconds'],
    ['Wait Until', '2/10/2014 2:25:00 AM', 'Wait until "TempPV(C)" >= 39'],
    ['Wait', '2/10/2014 2:36:33 AM', 'Wait 3600 seconds'],
    ['Wait Until', '2/10/2014 3:36:33 AM', 'Wait until "TempPV(C)" <= 28'],
    ['Set', '2/10/2014 3:36:33 AM', 'Set "TempModeUser" to Off'],
    ['Set', '2/10/2014 8:54:03 AM', 'Set "TempHeatDutyControl.PGain(min)" to 40'],
    ['Set', '2/10/2014 8:54:03 AM', 'Set "TempHeatDutyControl.ITime(min)" to 4.0'],
    ['Set', '2/10/2014 8:54:03 AM', 'Set "TempHeatDutyControl.DTime(min)" to 0'],
    ['Set', '2/10/2014 8:54:03 AM', 'Set "TempSP(C)" to 37'],
    ['Wait', '2/10/2014 8:54:03 AM', 'Wait 5 seconds'],
    ['Set', '2/10/2014 8:54:09 AM', 'Set "TempModeUser" to Auto'],
    ['Wait Until', '2/10/2014 8:54:09 AM', 'Wait until "TempPV(C)" >= 37'],
    ['Wait', '2/10/2014 10:43:00 AM', 'Wait 3600 seconds'],
    ['Set', '2/10/2014 11:43:01 AM', 'Set "TempSP(C)" to 39'],
    ['Wait', '2/10/2014 11:43:01 AM', 'Wait 5 seconds'],
    ['Wait Until', '2/10/2014 11:43:06 AM', 'Wait until "TempPV(C)" >= 39'],
    ['Wait', '2/10/2014 11:55:56 AM', 'Wait 3600 seconds'],

]


steps_report1_expected_test_steps = [
   ('2/7/2014 8:32:18 PM', '2/7/2014 10:05:19 PM', '2/7/2014 11:18:35 PM'),
    ('2/8/2014 4:39:54 AM', '2/8/2014 6:12:40 AM', '2/8/2014 7:24:45 AM'),
    ('2/8/2014 12:59:47 PM', '2/8/2014 2:32:15 PM', '2/8/2014 3:43:26 PM'),
    ('2/8/2014 9:41:17 PM', '2/8/2014 11:14:09 PM', '2/9/2014 12:24:45 AM'),
    ('2/9/2014 6:07:16 AM', '2/9/2014 7:40:46 AM', '2/9/2014 8:51:09 AM'),
    ('2/9/2014 3:16:07 PM', '2/9/2014 4:51:06 PM', '2/9/2014 6:02:05 PM'),
    ('2/10/2014 12:15:26 AM', '2/10/2014 2:24:54 AM', '2/10/2014 3:36:33 AM')

]


from datetime import datetime
from pbslib.batchutil import ParseDateFormat as parse
strptime = datetime.strptime

steps_report1_datetimes = []
fmt = ''
for t1, t2, t3 in steps_report1_expected_test_steps:
    fmt = parse(t1, fmt)

    tt1 = strptime(t1, fmt)
    tt2 = strptime(t2, fmt)
    tt3 = strptime(t3, fmt)

    steps_report1_datetimes.append((tt1, tt2, tt3))



