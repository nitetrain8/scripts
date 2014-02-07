"""
Created on Feb 5, 2014

@Company: PBS Biotech
@Author: Nathan Starkweather
"""


from officelib.pbslib.proxies import BatchFile, Parameter


class TestSettings():
    """ Container for settings of a PID test.
    """
    __slots__ = [
                 'Name',
                 'Pgain',
                 'Itime',
                 'Dtime',
                 'AutoMax',
                 'Setpoint'
                 ]
                 
    def __init__(self):
        self.Pgain = None
        self.Itime = None
        self.Dtime = None
        self.AutoMax = None
        self.Setpoint = None


# noinspection PyMethodMayBeStatic
class TpidTest():
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
        
        self._settings = None
        self._temppv = None
        self._heatduty = None
        self._filename = filename
        
        self._process(filename)

    def _process(self, filename: str) -> None:
        """
        @param filename: same as init
        @return: None
        """

        batch = BatchFile(filename)
        
        self._build_settings(batch)
        self._extract_data(batch)

    @property
    def Settings(self) -> TestSettings:
        """
        @return: test's settings
        """
        return self._settings

    def _extract_data(self, batch: BatchFile) -> None:
        
        self._temppv = batch['TempPV(C)']
        self._heatduty = batch['TempHeatDutyActual(%)']
        
    def _build_settings(self, batch: BatchFile):
        
        """ Assign settings for the test from
        the BatchFile object passed.

        """

        settings = TestSettings()
        
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
        
        
class TestEntry():

    def __init__(self):

        self._settings = None

        self._temp_times = None
        self._temp_pvs = None

        self._topleft = None

        
        
        
        
        
        
        
        

