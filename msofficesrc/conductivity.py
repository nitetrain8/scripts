"""
Created on Jan 27, 2014

@Company: PBS Biotech
@Author: Nathan Starkweather

Refactor of msofficesrc/mixingtime.py.

After looking at the original, it was holy balls bad.
SO BAD. Kill myself bad. Live, learn, refactor.

"""

from officelib.olutils import getDownloadDir
from tkinter.filedialog import askopenfilenames
from officelib.xllib.xlcom import Excel  # @UnresolvedImport
from officelib.xllib.xladdress import cellStr  # @UnresolvedImport
from officelib.pbslib.proxies import BatchFile  # @UnresolvedImport
from itertools import zip_longest


def mean(list_):
    """ Naive mean for simple things"""
    return sum(list_) / len(list_)


def ask_user_for_files():
    """ Ask the user what files they'd like to
    analyze. This function should be the frontend
    for getting information from user, including list
    of all files to manage, and any other options.

    If necessary, let this function grow into a class.

    @return: list of filenames
    @rtype: list of strings
    """
    
    try:
        initialdir = getDownloadDir()
    except:
        initialdir = "C:/Users/Public/Documents"
    filetypes = ["{CSV} {.csv}"]
    tcl_filestring = askopenfilenames(initialdir=initialdir,
                                      multiple=True,
                                      filetypes=filetypes)
    files = tcl_filestring.strip("{}").split("} {")
    return files
    
    
class ConductivityTest(BatchFile):
    """ Object representing the individual conductivity tests.

    A conductivity test is a batch file, with a few extra
    methods for calculating test-specific values.
    """
    
    def __init__(self, filename=None):
        super().__init__(filename)
        
        self.logger_start_index, self.test_start_time = self.calculate_start_time()
        self.test_parameter = self.find_conductivity_parameter()
                                            
        self.StartMeasure = self.raw_start_measure()
        self.EndMeasure = self.raw_end_measure()
        self.DeltaMeasure = self.EndMeasure - self.StartMeasure 
    
    def calculate_start_time(self):
        
        try:
            logger_start_index, start_time = next((i, time) for i, (time, value) 
                                            in enumerate(self["LoggerMaxLogInterval(ms)"])
                                                if value == 1000)
        except StopIteration:
            raise ValueError("Invalid test data- no 1000 ms Logger Time found")
        
        return (logger_start_index, start_time)
    
    def find_conductivity_parameter(self):
        """ Determine which column is used to store
        conductivity values. Currently, either phA
        or phB is used as a proxy to record the raw
        voltage output by the conductivity probe.

        If both are recorded in a batch file, try and
        guess the one that is being used. A typical test
        according to IP00043 Rev A results in an increase
        of approximately 0.25V from start to finish, so a
        the one which shows a value closest to that is probably
        the one.

        @return: name of column used for conductivity
        @rtype: str

        """
        
        pHA = self.get('pHARaw', None)
        pHB = self.get('pHBRaw', None)
        
        # If only one, return the one.
        
        if bool(pHA) != bool(pHB):  # XOR
            return pHA.name if pHA else pHB.name
        
        def mean(list_):
            return sum(list_) / len(list_)
        
        #average first 5 and last values
        
        pHA_delta = self._value_delta(pHA)
        pHB_delta = self._value_delta(pHB)
        
        smallest = min(abs(pHA_delta), abs(pHB_delta))
        
        if smallest == pHA_delta:
            return pHA
        else:
            return pHB
    
    def _value_delta(self, param):
        """ Helper func for calculating the delta of
        parameter values

        @param param: proxies.Parameters object
        @return: float
        """
        
        values = param.values
        start = values[:5]
        end = values[-5:]
        
        return mean(end) - mean(start)
        
    def py2xlAddress(self, index, parameter):
        
        """ Get excel $A$1 style cell address for the
        given parameter in the spreadsheet
        """
        
        column = self.py2xlColumn(parameter)
        row = index + 2
        
        return cellStr(row, column, 1, 1)

    def build_elapsed_time_col(self, reference, date_column, rows):
        
        formula = "=(%s - %s) * 60 * 60 * 24" % ('%s', reference)
        
        def fmt_tmplt(row, formula=formula, date_column=date_column, cellStr=cellStr):
            return formula % cellStr(row, date_column)
        
        data = [fmt_tmplt(row) for row in range(2, rows + 2)]
        
        return data
        
    def raw_start_measure(self):
        return self.test_parameter.AverageStartValues(n=5)
    
    def raw_end_measure(self):
        
        times = self.test_parameter.Times.ElapsedTimes
        end_time = times[-1]
        
        end_time_start = next(i for i, time in enumerate(reversed(times)) if time < 80)
        
        return self.test_parameter.AverageEndValues(n=end_time_start)
        
    def find_first(self, iterable, cb):
        return next(i for i, value in enumerate(iterable) if cb(value))
        
    def conductivity_range(self):
        start_conductivity = self.raw_start_measure()
        end_conductivity = self.raw_end_measure()
        
        return start_conductivity, end_conductivity
        
    def PlotRaw(self, ws):
        """ Plot the raw data, plus the elapsed
        time column.
        """
        
        test_param = self.test_parameter
        self.move_to_end(test_param.name)       
        
        start_time_cell = self.py2xlAddress(self.logger_start_index, 
                                    "LoggerMaxLogInterval(ms)")
        self.start_time_cell = start_time_cell
        
        headers, data = self.xlColumns()
        
        rows = len(test_param)
        column = self.py2xlColumn(test_param.name)
        
        time_column = self.build_elapsed_time_col(start_time_cell, column, rows)

        data.insert(-2, time_column)
        headers.insert(-2, 'ElapsedTime')
        data = list(zip_longest(*data))  # column -> row order
        
        self.plotdata(ws, headers, data)
        
    def PlotAnalysis(self, ws):
        
        self.PlotRaw(ws)
        
        start, end = self.conductivity_range()
        delta = end - start
        max_hysteresis = 0.05 * delta 
        conductivity = self.test_parameter
        
        def isSettled(pv):
            return abs(pv - end) <= max_hysteresis
    
        # scan backwards for last_index index, add 1 if 0 to avoid OOB, convert rev -> fwd index
        
        last_index = next(i for i, pv in enumerate(reversed(conductivity.Values)) if not isSettled(pv))
        last_index = last_index or 1 
        last_index = len(conductivity.Values) - last_index
        
        table = [
                 ("Conductivity T=0", "Conductivity T=f", "Delta Conductivity", "5.0%"),
                 (str(self.StartMeasure), str(self.EndMeasure), str(self.DeltaMeasure), max_hysteresis)
                 ]
                 
        columns = self.ColumnCount + 1
        start_col = columns + 2
        end_col = start_col + len(table[0]) - 1
        
        cells = ws.Cells
    
        table_start = cells(1, start_col)
        table_end = cells(len(table), end_col)
        
        cells.Range(table_start, table_end).Value = table
        
        

def analyze_files(xl, files):
    """ toWorksheet the files using xl application
    @param xl: win32com Excel application object
    @param files: list of filenames

    """

    for file in files:
        test = ConductivityTest(file)
        
        ws = xl.Workbooks.Add().Worksheets(1)
        
        test.PlotAnalysis(ws)
        
        
        
        
        
        
        
#         wb = xl.Workbooks.Add()
#         ws = wb.Worksheets(1)
#         test.toWorksheet(ws)
#         print(start_time)
        
    
def main():
    
#     files = ask_user_for_files()
    # debug 
    files = [
            "C:/Users/PBS Biotech/Downloads/conductivity/mt 1.2.csv", 
            "C:/Users/PBS Biotech/Downloads/conductivity/mt 1.3.csv"
            ]
    
    xl = Excel(new=True, visible=False)
    wb = xl.Workbooks.Add()
    # try/finally around xl
    try:
        analyze_files(xl, files)
    finally:
        xl.Visible = True
        
    
if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
