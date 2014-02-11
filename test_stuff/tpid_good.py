"""
Created on Jan 23, 2014

@Company: PBS Biotech
@Author: Nathan Starkweather

Methods related to performing analysis for
temperature-PID tuning.

"""
from officelib.pbslib.proxies import BatchFile  # @UnresolvedImport
from officelib.pbslib.batchutil import FilterIndexRange  # @UnresolvedImport
from itertools import zip_longest
from os.path import split as path_split
from officelib.olutils import ListFullDir as ol_ListFullDir
from officelib.xllib.xlcom import xlBook, EnsureDispatch  # @UnresolvedImport
from officelib.const import xlByColumns, xlByRows  # @UnresolvedImport
from officelib.xllib.xladdress import cellRangeStr, cellStr  # @UnusedImport @UnresolvedImport


class TestHandler():
    
    """ This class represents an entire series of tests
    in a single worksheet.

    TestHandler.Register(PIDTest) -> Register a test with
    the testhandler.

    """
    
    def __init__(self, wb, SaveAsName=None):
        """ Initialize the test with the
        excel workbook wb, naming the file
        SaveAsName. If SaveAsName is None,
        the workbook's existing name is used

        """
        
        self.xl = wb.Application
        self.wb = wb
        
        if not wb.Worksheets.Count:
            wb.Worksheets.Add(1)
        self.ws = wb.Worksheets(1)
        self.cells = self.ws.Cells
        self.cell_range = self.cells.Range
        
        if SaveAsName is None:
            SaveAsName = wb.Name
        self.SaveAsName = SaveAsName
        
        self._tests = []
        self._worksheet_index = {} 
        
        self.TestSP = 37
        
        self.create_control_header()
        self.create_control_data()
        
    def Register(self, test):
        """ Register a test with the handler.
        The data will be added to the worksheet
        later.

        """
        self._tests.append(test)
        
    def RegisterFromFilename(self, filename):
        test = PIDTest(filename)
        self._tests.append(test)
        
    def RegisterFromDir(self, dirname):
        
        for file in ol_ListFullDir(dirname):
            test = PIDTest(file)
            self._tests.append(test)
        
    def create_control_header(self):
        """ Create the control header in the first three columns of the
        worksheet.

        """
        
        control_header = (
                          ("Control", None, None),
                          (None, None, None),
                          ('Ave_m', 'Ave_b', 'offset'),
                          (None, None, None),
                          ('SP', None, None),
                          (self.TestSP, None, None),
                          ("Ideal Time", "Ideal Temp", None)
                          )
                          
        self.header_width = max([len(i) for i in control_header])
        self.header_height = len(control_header)
        
        header_range = cellRangeStr(
                                     (1,1),
                                     (self.header_height, self.header_width)
                                     )
                                    
        self.cell_range(header_range).Value = control_header
        
    def create_control_data(self):
        """ Create the set of control data at the
        beginning of the test.

        If class is extended, magic numbers may need to be
        updated.

        """
        
        # Cell coordinates in form of cellStr() args
        ave_m_cell = (5, 1, 0, 1)
        ave_b_cell = (5, 2, 0, 1)
        ideal_sp_cell = (6, 1, 1, 1)
        
        ideal_formula = '=MIN(%s*%s+%s,%s)' % (cellStr(*ave_m_cell),
                                               '%s',
                                               cellStr(*ave_b_cell),
                                               cellStr(*ideal_sp_cell))
        
        ideal_seconds = 10000
        
        ideal_data = [(i, ideal_formula % cellStr(i + self.header_height, 1))
                        for i in range(1, ideal_seconds + 1)]
        
        ideal_range = cellRangeStr(
                                   (8, 1),
                                   (ideal_seconds + 7, 2)
                                   )
                                   
        self.cell_range(ideal_range).Value = ideal_data
        
    @staticmethod
    def count_worksheet_tests(ws):
    
        """ Count the number of tests present in the worksheet,
        based on the number of headers counted.

        """
        
        results = set()
        cells = ws.Cells
        
        result = cells.Find(What='Name:', SearchOrder=xlByColumns)
        while result and (result.Row, result.Column) not in results:
            results.add((result.Row, result.Column))
            result = cells.FindNext(result)
            
        return len(results)

    def _plot_test(self, row, column, test):
        
        header = test.RawHeader()
        data = test.RawData()
        rows, columns = test.Size()
        
        end_col = column + columns - 1
        
        header_range = cellRangeStr(
                                    (1, column), 
                                    (len(header), end_col))
        data_range = cellRangeStr(
                                    (len(header) + 1, column), 
                                    (rows, end_col))
                                    
        self.cell_range(header_range).Value = header
        self.cell_range(data_range).Value = data

    def PlotAll(self):
        
        column = 4  # Update by number of tests plotted later
        for test in self._tests:
            
            self._plot_test(1, column, test)
            column += test.Size()[1] + 1
            
            
        
    
        
#     def build_worksheet_index(self):
#         ''' Index all the tests in the worksheet.
#         Use this to resume previous sessions.'''
#         
#         tests = {}
#         checked = set()
#         cells = self.Cells
#         
#         result = cells.Find(What='Name:', SearchOrder=xlByColumns)
#         
#         if result is None:
#             self._worksheet_index = {}
#             return
#         
#         header_cell_coords = (
#                        ("Name", (1,2)),
#                        ("Pgain", (2,2)),
#                        ("Itime", (3,2)),
#                        ("Dtime", (4,2)),
#                        ("AutoMax", (5,2)),
#                        ("SP", (6,2)),
#                        ("m", (3,5)),
#                        ('b', (3,6)),
#                        ('x_shift', (3,7)),
#                        ('Max', (4,6)),
#                        ('Central', (4,7))
#                        )
#         
#         while result and (result.Row, result.Column) not in checked:
#             checked.add((result.Row, result.Column))
             
        
        
        
    
class PIDTest():
    """ This class represents the test context itself,
    after raw file processing.

    PIDTest(filename) -> data to be pasted into
    a spreadsheet containing information about the test
    (name, gain settings, etc), and the processed
    information.

    Each PIDTest is bound to a single test file.

    """
    
    def __init__(self, filename):
        
        """ Declare and initialize instance variables, to be filled in
        by appropriate functions at the appropriate times.

        heat duty and temp pv are stored as properties, to prevent
        accidentally overriding them. The attributes are accessed
        simply by using an underscore before the name.

        """
        
        # These settings variables are public so that they 
        # can be changed easily if data pulled from the batch
        # file is incomplete or inaccurate.
        
        self.Name = None
        self.Pgain = None
        self.Itime = None
        self.Dtime = None
        self.AutoMax = None
        self.SP = None
        self.LinearStartTemp = None
        self.LinearEndTemp = None
        
        self._TempPV = None
        self._HeatDuty = None
        self._filename = None
        self._start_row = None
        self._data_start_row = None
        self._end_row = None
        self._start_column = None
        self._end_column = None
        self._columns = 7
        self._header_rows = 7 
        
        self.process_file(filename)
        
    @property
    def TempPV(self):
        return self._TempPV
    
    @property
    def HeatDuty(self):
        return self._HeatDuty
    
    def process_file(self, filename):
        
        """ Open the file for processing, extract
        settings and data. This function is called
        automatically by __init__ if when passed a
        filename.

        Pass around batch file as a parameter,
        then discard it to save data space.

        """
        self._filename = filename
        batch = BatchFile(filename)
        self._build_settings(batch)
        
        if not self.LinearStartTemp:
            self.LinearStartTemp = 29.5
            
        if not self.LinearEndTemp:
            self.LinearEndTemp = 35
        
        self._extract_data(batch)
        
        self._calculate_linear_range()
        self.setTopLeft(1,1)
        
    def _extract_data(self, batch):
        
        """ Extract the relevant data from the batch file
        and assign relevant parameters to self.

        """
        
        self._TempPV = batch['TempPV(C)']
        self._HeatDuty = batch['TempHeatDutyActual(%)']
        
    def _calculate_linear_range(self):
        
        """ Get the index of linear data range.
        This is useful to have calculated and lying around.

        """
        
        linear_range = lambda temp: self.LinearStartTemp < temp < self.LinearEndTemp
        linear_start, linear_end = FilterIndexRange(self._TempPV.Values, linear_range)
        
        self._linear_start_index = linear_start or 0
        self._linear_end_index = linear_end or len(self._TempPV) - 1
        
    def _build_settings(self, batch):
        
        """ Assign settings for the test from
        the BatchFile object passed.

        """
        
        # Because some non-critical information might not be
        # available in the batch file, set default values
        # if keyerror.  
        
        float2str = lambda x: str(x).rstrip('0').rstrip('.') 
        name = ''
        
        gain_settings = (
                     ('Pgain', "TempHeatDutyControl.PGain(min)"),
                     ('Itime', 'TempHeatDutyControl.ITime(min)'),
                     ("Dtime", 'TempHeatDutyControl.DTime(min)')
                     )

        for attr, key in gain_settings:
            try:
                setting = batch[key].Values.mode
                name += attr[0].lower() + float2str(setting)
            except KeyError:
                setting = '0.0'
                
            setattr(self, attr, setting)
            
        # These can be guessed by looking at a corresponding PV value
        
        try:
            self.AutoMax = batch['TempHeatDutyAutoMax(%)'].Values.mode
        except KeyError:
            self.AutoMax = int(max(batch['TempHeatDutyActual(%)'].Values)) 
            
        try:
            self.SP = batch['TempSP(C)'].Values.mode
        except KeyError:
            self.SP = batch['TempPV(C)'].AverageStartValues(n=10)
        
        if not name:
            name = "<noname>"
        
        self.Name = name
        
    def setTopLeft(self, row=1, column=1):
        
        self._start_row = row
        self._data_start_row = row + self._header_rows
        self._end_row = row + len(self) - 1
        self._start_column = column
        self._end_column = column + self._columns - 1
        
    def Size(self):
        rows = len(self)
        columns = self._columns
        return rows, columns
        
    def __len__(self):
        return self._header_rows + max(len(self._TempPV), len(self._HeatDuty))
        
    def RawHeader(self):
        """ Build the raw header for the test as a tuple of tuples
        (inner tuples are rows).

        This format allows the header to be set directly into
        a worksheet by calculating rows=len(tuple), cols = len(tuple[0])
        """
        
        filename = path_split(self._filename)[1]
        
        header = (
               ('Name:', self.Name, filename, None, None, None, None),
               ('Settings:', 'P', self.Pgain, None, 'm', 'b', 'x-shift'),
               (None, 'I', self.Itime, None, None, None, None),
               (None, 'D', self.Dtime, None, None, 'Max', 'Central'),
               (None, 'AutoMax', self.AutoMax, None, None, None, None),
               (None, 'SP', self.SP, None, None, None, None),
               ('TempTime', 'ElapsedTime', 'NormalizedTime', 'TempValue', None, 'HeatDutyTime', 'HeatDutyValue')
                )
        return header
        
    def RawData(self):
        """ Build the raw data block as a tuple of tuples.
        this version does not build the formulas used to calculate
        elapsed time or normalized time, and leaves those columns empty.
        Thus, it is location-agnostic.
        """
        
        temp = self._TempPV
        heat = self._HeatDuty
        data = tuple(zip_longest(temp.times.Datestrings, 
                                [None], 
                                [None], 
                                temp.values, 
                                [None], 
                                heat.times.Datestrings, 
                                heat.values, fillvalue=None))
    
        return data
        
        
        
def main():
    pass
    
        
if __name__ == '__main__':
#     wb = xlBook("compiledbackup2.xlsx")
#     ws = wb.Worksheets(1)
#     print(TestHandler.count_worksheet_tests(ws))
    testfile = "C:/Users/PBS Biotech/Documents/Personal/test files/tpid/tpid_test.xlsx"
    testdir = "C:/Users/PBS Biotech/Documents/Personal/test files/tpid/raw"
    
#     xl = EnsureDispatch('Excel.Application')
#     wb = xl.Workbooks()
    wb = xlBook(testfile)
#     
    t = TestHandler(wb)
    t.RegisterFromDir(testdir)
    t.PlotAll()
        
        
        
