"""
Created on Feb 5, 2014

@Company: PBS Biotech
@Author: Nathan Starkweather
"""
from itertools import zip_longest

from pbslib.datareport import DataReport, Parameter
from officelib.xllib.xladdress import cellStr as _cellStr


class Settings():
    """ Container for settings of a PID test.
    """
    __slots__ = [
                 'Name',
                 'Filename',
                 'Pgain',
                 'Itime',
                 'Dtime',
                 'AutoMax',
                 'Setpoint'
                 ]
                 
    def __init__(self):
        self.Name = None
        self.Filename = None
        self.Pgain = None
        self.Itime = None
        self.Dtime = None
        self.AutoMax = None
        self.Setpoint = None


# noinspection PyMethodMayBeStatic
class RawTPID():
    """ This class represents the test data,
    after raw file processing, before analysis.

    TpidTest(filename) -> data to be pasted into
    a spreadsheet containing information about the test
    (name, gain settings, etc), and the processed
    information.

    Each TpidTest is bound to a single test file.

    """

    # # max logger time is used as an indicator of
    # # test starting
    # max_logger_sentinel = 123321
    
    def __init__(self, filename: str):
        """
        @param filename: raw batch file to open
        @return: None
        """

        self._filename = filename
        self._process_filename(filename)

    def _process_filename(self, filename: str) -> None:
        """
        @param filename: same as init
        @return: None
        """
        batch = DataReport(filename)
        self._process_batch(batch)

    def _process_batch(self, batch: DataReport) -> None:
        self._build_settings(batch)
        self._extract_data(batch)

    @classmethod
    def fromBatch(cls, batch: DataReport):
        """
        @param batch: batch file to build test entry from
        @return: new instance of RawTPID
        """
        self = cls.__new__(cls)
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        self._process_batch(batch)
        return self

    @property
    def Settings(self) -> Settings:
        """
        @return: test's settings
        """
        return self._settings

    def _extract_data(self, batch: DataReport) -> None:
        
        self._temppv = batch['TempPV(C)']
        self._heatduty = batch['TempHeatDutyActual(%)']
        
    def _build_settings(self, batch: DataReport) -> None:
        
        """ Assign settings for the test from
        the DataReport object passed.

        """

        settings = Settings()
        
        settings.Pgain = batch.get("TempHeatDutyControl.PGain(min)", '0.0')
        settings.Itime = batch.get("TempHeatDutyControl.ITime(min)", '0.0')
        settings.Dtime = batch.get("TempHeatDutyControl.DTime(min)", '0.0')

        settings.Name = ''.join((
                                'p',
                                settings.Pgain,
                                'i',
                                settings.Itime,
                                'd',
                                settings.Dtime
                                ))

        settings.Filename = batch.Filename
            
        # These can be guessed by looking at a corresponding PV value
        
        try:
            settings.AutoMax = batch['TempHeatDutyAutoMax(%)'].AverageStartValues(n=3)
        except KeyError:
            settings.AutoMax = int(max(batch['TempHeatDutyActual(%)'].Values))
            
        try:
            settings.Setpoint = int(batch['TempSP(C)'].AverageStartValues(n=3))
        except KeyError:
            settings.Setpoint = int(batch['TempPV(C)'].AverageEndValues(n=10)) - 2

        self._settings = settings
        
    @property
    def TempPV(self) -> Parameter:
        """

        @return: TempPV parameter
        """
        return self._temppv
        
    @property
    def HeatDuty(self) -> Parameter:
        """

        @return: HeatDutyActual parameter
        """
        return self._heatduty
        
        
class xlEntry():

    HEADER_LEN = 7

    def __init__(self):

        self._settings = None

        self._temp_times = None
        self._temp_pvs = None

        self._heat_times = None
        self._heat_pvs = None

        self._top_left_address = None
        self._top_left_coords = None
        self._linear_start_cell = None
        self._linear_end_cell = None

    @property
    def TopLeftCoords(self) -> tuple:
        return self._top_left_coords

    @property
    def TopLeftAddress(self) -> str:
        return self._top_left_address

    @property
    def Settings(self) -> Settings:
        return self._settings

    @property
    def TempTimes(self) -> list:
        return self._temp_times

    @property
    def TempValues(self) -> list:
        return self._temp_pvs

    @property
    def HeatTimes(self) -> list:
        return self._heat_times

    @property
    def HeatValues(self) -> list:
        return self._heat_pvs

    @classmethod
    def fromFile(cls, filename: str, top_left: tuple=(1, 1)):
        """

        @param filename: filename of raw batch file to open
        @param top_left: cell coordinates (row, column) of topleft
                        cell in excel sheet.
        @return: New instance of xlEntry
        """

        test = RawTPID(filename)
        return cls.fromTest(test, top_left)

    @classmethod
    def fromTest(cls, tpid_test: RawTPID, top_left: tuple=(1, 1)):
        """
        @param tpid_test: RawTPID instance to make test entry from
        @param top_left: cell coordinates (row, column) of topleft
                cell in excel sheet.
        @return: new instance of xlEntry
        """
        self = cls()
        self._settings = tpid_test.Settings
        self._top_left_coords = top_left
        self._top_left_address = _cellStr(*top_left)

        self._temp_times = tpid_test.TempPV.Times.Datestrings
        self._temp_pvs = tpid_test.TempPV.Values

        self._heat_times = tpid_test.HeatDuty.Times.Datestrings
        self._heat_pvs = tpid_test.HeatDuty.Values

        return self

    @classmethod
    def fromBatch(cls, batch: DataReport, top_left: tuple=(1, 1)):
        """
        @param batch: RawTPID instance to make test entry from
        @param top_left: cell coordinates (row, column) of topleft
                cell in excel sheet.
        @return: new instance of xlEntry
        """

        test = RawTPID.fromBatch(batch)
        return cls.fromTest(test, top_left)

    def toWorksheet(self, ws):

        s = self.Settings
        header = (
               ('Name:', s.Name, s.Filename, None, None, None, None),
               ('Settings:', 'P', s.Pgain, None, 'm', 'b', 'x-shift'),
               (None, 'I', s.Itime, None, None, None, None),
               (None, 'D', s.Dtime, None, None, 'Max', 'Central'),
               (None, 'AutoMax', s.AutoMax, None, None, None, None),
               (None, 'SP', s.Setpoint, None, None, None, None),
               ('TempTime', 'ElapsedTime', 'NormalizedTime', 'TempValue', None, 'HeatDutyTime', 'HeatDutyValue')
                )

    def _build_xl_data(self):

        temp_elapsed = self._build_elapsed_times(self.TempTimes, 1)
        heat_elapsed = self._build_elapsed_times(self.HeatTimes, 6)
        temp_normalized = self._build_normalized_times(self.TempTimes, 2)

        basic = zip_longest(
                            self.TempTimes,
                            temp_elapsed,
                            temp_normalized,
                            self.TempValues,
                            [None],
                            self.HeatTimes,
                            heat_elapsed,
                            self.HeatValues,
                            )

    def _build_elapsed_times(self, times: list, col_offset: int, cellStr=_cellStr) -> list:

        start_row, col = self.TopLeftCoords
        start_row += self.HEADER_LEN
        data_ref_cell = cellStr(start_row, col, 1, 1)
        ref_formula = data_ref_cell.join(("=(%s -", ") % 1440"))

        col += col_offset

        rows = len(times)
        end_row = start_row + rows

        return (ref_formula % cellStr(row, col) for row in range(start_row, end_row + 1))

    def _build_normalized_times(self, times: list, col_offset: int, cellStr=_cellStr) -> list:

        start_row, col = self.TopLeftCoords
        start_row += self.HEADER_LEN

        rows = len(times)
        end_row = start_row + rows

        col = col_offset - 1

        return ("=" + cellStr(row, col) for row in range(start_row, end_row + 1))


        
        

        

