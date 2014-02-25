"""

Created by: Nathan Starkweather
Created on: 02/25/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

recipe1 = [
            ["Step Type", "Date Time", "Step Name"],
            ["Wait Until", "3/17/2014 21:55", "Wait until \"TempPV(C)\" <= 28"],
            ["Set", "3/17/2014 21:55", "Set \"TempModeUser\" to Off"],
            ["Set", "3/18/2014 0:54", "Set \"TempHeatDutyControl.PGain(min)\" to 40"],
            ["Set", "3/18/2014 0:54", "Set \"TempHeatDutyControl.ITime(min)\" to 4.0"],
            ["Set", "3/18/2014 0:54", "Set \"TempHeatDutyControl.DTime(min)\" to 0"],
            ["Set", "3/18/2014 0:54", "Set \"TempSP(C)\" to 37"],
            ["Wait", "3/18/2014 0:54", "Wait 5 seconds"],
            ["Set", "3/18/2014 0:54", "Set \"TempModeUser\" to Auto"],
            ["Wait Until", "3/18/2014 0:54", "Wait until \"TempPV(C)\" >= 37"],
            ["Wait", "3/18/2014 2:36", "Wait 3600 seconds"],
            ["Wait", "3/18/2014 3:36", "Wait 5 seconds"],
            ["Set", "3/18/2014 3:36", "Set \"TempSP(C)\" to 39"],
            ["Wait Until", "3/18/2014 3:36", "Wait until \"TempPV(C)\" >= 39"],
            ["Wait", "3/18/2014 3:49", "Wait 3600 seconds"],
            ["Set", "3/18/2014 4:49", "Set \"TempModeUser\" to Off"],
            ["Wait", "3/18/2014 4:49", "Wait 5 seconds"],
            ["Wait Until", "3/18/2014 4:50", "Wait until \"TempPV(C)\" <= 28"],
            ["Set", "3/18/2014 5:36", "Set \"TempModeUser\" to Off"],
            ["Wait", "3/18/2014 5:36", "Wait 5 seconds"],
            ["Set", "3/18/2014 5:36", "Set \"TempSP(C)\" to 30"],
            ["Wait", "3/18/2014 5:36", "Wait 5 seconds"],
            ["Set", "3/18/2014 5:36", "Set \"TempModeUser\" to Auto"],
            ["Wait", "3/18/2014 5:36", "Wait 5 seconds"],
            ["Wait Until", "3/18/2014 5:36", "Wait until \"TempPV(C)\" <= 28"],
            ["Set", "3/18/2014 5:36", "Set \"TempModeUser\" to Off"],
            ["Wait Until", "3/18/2014 5:36", "Wait until \"TempPV(C)\" > 29"],
            ["Set", "3/18/2014 12:23", "Set \"TempHeatDutyControl.ITime(min)\" to 4.5"],
            ["Set", "3/18/2014 12:23", "Set \"TempHeatDutyControl.DTime(min)\" to 0"],
            ["Set", "3/18/2014 12:23", "Set \"TempSP(C)\" to 37"],
            ["Wait", "3/18/2014 12:23", "Wait 5 seconds"],
            ["Set", "3/18/2014 12:23", "Set \"TempHeatDutyControl.PGain(min)\" to 45"],
            ["Set", "3/18/2014 12:23", "Set \"TempModeUser\" to Auto"],
            ["Wait Until", "3/18/2014 12:23", "Wait until \"TempPV(C)\" >= 37"],
            ["Wait", "3/18/2014 14:44", "Wait 3600 seconds"],
            ["Set", "3/18/2014 15:44", "Set \"TempSP(C)\" to 39"],
            ["Wait", "3/18/2014 15:44", "Wait 5 seconds"],
            ["Wait Until", "3/18/2014 15:44", "Wait until \"TempPV(C)\" >= 39"],
            ["Wait", "3/18/2014 17:12", "Wait 3600 seconds"],
            ["Wait", "3/18/2014 18:12", "Wait 5 seconds"],
            ["Set", "3/18/2014 18:12", "Set \"TempModeUser\" to Off"],
            ["Wait Until", "3/18/2014 18:12", "Wait until \"TempPV(C)\" <= 28"],
            ["Set", "3/18/2014 22:53", "Set \"TempHeatDutyControl.PGain(min)\" to 50"],
            ["Set", "3/18/2014 22:53", "Set \"TempHeatDutyControl.ITime(min)\" to 5.0"],
            ["Set", "3/18/2014 22:53", "Set \"TempHeatDutyControl.DTime(min)\" to 0"],
            ["Set", "3/18/2014 22:53", "Set \"TempSP(C)\" to 37"],
            ["Wait", "3/18/2014 22:53", "Wait 5 seconds"],
            ["Set", "3/18/2014 22:53", "Set \"TempModeUser\" to Auto"],
            ["Wait Until", "3/18/2014 22:53", "Wait until \"TempPV(C)\" >= 37"],
            ["Wait", "3/19/2014 1:01", "Wait 3600 seconds"],
            ["Wait", "3/19/2014 2:01", "Wait 5 seconds"],
            ["Set", "3/19/2014 2:01", "Set \"TempSP(C)\" to 39"],
            ["Wait Until", "3/19/2014 2:01", "Wait until \"TempPV(C)\" >= 39"],
            ["Wait", "3/19/2014 3:23", "Wait 3600 seconds"],
            ["Set", "3/19/2014 4:23", "Set \"TempModeUser\" to Off"],
            ["Wait", "3/19/2014 4:23", "Wait 5 seconds"],
            ["Wait Until", "3/19/2014 4:23", "Wait until \"TempPV(C)\" <= 28"],
            ["Wait", "3/19/2014 10:53", "Wait 5 seconds"],
            ["Set", "3/19/2014 10:53", "Set \"TempHeatDutyControl.PGain(min)\" to 55"],
            ["Set", "3/19/2014 10:53", "Set \"TempHeatDutyControl.ITime(min)\" to 5.5"],
            ["Set", "3/19/2014 10:53", "Set \"TempHeatDutyControl.DTime(min)\" to 0"],
            ["Set", "3/19/2014 10:53", "Set \"TempSP(C)\" to 37"],
            ["Set", "3/19/2014 10:53", "Set \"TempModeUser\" to Auto"],
            ["Wait Until", "3/19/2014 10:53", "Wait until \"TempPV(C)\" >= 37"],
            ["Wait", "3/19/2014 13:24", "Wait 3600 seconds"],
            ["Set", "3/19/2014 14:24", "Set \"TempSP(C)\" to 39"],
            ["Wait", "3/19/2014 14:24", "Wait 5 seconds"],
            ["Wait Until", "3/19/2014 14:25", "Wait until \"TempPV(C)\" >= 39"],
            ["Wait", "3/19/2014 16:03", "Wait 3600 seconds"],
            ["Set", "3/19/2014 17:03", "Set \"TempModeUser\" to Off"],
            ["Wait", "3/19/2014 17:03", "Wait 5 seconds"],
            ["Wait Until", "3/19/2014 17:03", "Wait until \"TempPV(C)\" <= 28"],
            ["Set", "3/19/2014 21:02", "Set \"TempSP(C)\" to 37"],
            ["Wait", "3/19/2014 21:02", "Wait 5 seconds"],
            ["Set", "3/19/2014 21:02", "Set \"TempHeatDutyControl.ITime(min)\" to 6.0"],
            ["Set", "3/19/2014 21:02", "Set \"TempHeatDutyControl.PGain(min)\" to 60"],
            ["Set", "3/19/2014 21:02", "Set \"TempHeatDutyControl.DTime(min)\" to 0"],
            ["Wait Until", "3/19/2014 21:02", "Wait until \"TempPV(C)\" >= 37"],
            ["Set", "3/19/2014 21:02", "Set \"TempModeUser\" to Auto"],
            ["Wait", "3/19/2014 23:23", "Wait 3600 seconds"],
            ["Wait", "3/20/2014 0:23", "Wait 5 seconds"],
            ["Set", "3/20/2014 0:23", "Set \"TempSP(C)\" to 39"],
            ["Wait Until", "3/20/2014 0:23", "Wait until \"TempPV(C)\" >= 39"],
            ["Wait", "3/20/2014 2:11", "Wait 3600 seconds"],
            ["Set", "3/20/2014 3:11", "Set \"TempModeUser\" to Off"],
            ["Wait", "3/20/2014 3:11", "Wait 5 seconds"],
            ["Wait Until", "3/20/2014 3:11", "Wait until \"TempPV(C)\" <= 28"],
            ["Set", "3/20/2014 9:55", "Set \"TempHeatDutyControl.PGain(min)\" to 65"],
            ["Wait", "3/20/2014 9:55", "Wait 5 seconds"],
            ["Set", "3/20/2014 9:55", "Set \"TempSP(C)\" to 37"],
            ["Set", "3/20/2014 9:55", "Set \"TempHeatDutyControl.ITime(min)\" to 6.5"],
            ["Set", "3/20/2014 9:55", "Set \"TempHeatDutyControl.DTime(min)\" to 0"],
            ["Set", "3/20/2014 9:55", "Set \"TempModeUser\" to Auto"],
            ["Wait Until", "3/20/2014 9:55", "Wait until \"TempPV(C)\" >= 37"],
            ["Wait", "3/20/2014 12:48", "Wait 3600 seconds"],
            ["Set", "3/20/2014 13:48", "Set \"TempSP(C)\" to 39"],
            ["Wait", "3/20/2014 13:48", "Wait 5 seconds"],
            ["Wait Until", "3/20/2014 13:48", "Wait until \"TempPV(C)\" >= 39"],
            ["Wait", "3/20/2014 15:51", "Wait 3600 seconds"],
            ["Set", "3/20/2014 16:51", "Set \"TempModeUser\" to Off"],
            ["Wait", "3/20/2014 16:51", "Wait 5 seconds"],
            ["Wait Until", "3/20/2014 16:51", "Wait until \"TempPV(C)\" <= 28"],
    ]