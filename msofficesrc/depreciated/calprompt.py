"""
Created on Dec 12, 2013

@author: PBS Biotech
"""
import tkinter as tk
import tkinter.ttk as ttk
from os import makedirs
from os.path import exists
from sys import exit
from officelib import xllib


class DialogIncompleteError(Exception):
    pass
    
    
'''This whole module should be refactored to be a single class
that does all the work of both classes and all functions. Current
implementation requires linking functions together awkwardly 
in a predefined order, with no master function other than 'main'
to do all the work for us.'''

FUNC_TEST_FOLDER = "C:\\Users\\Public\Documents\\PBSSS\\Functional Testing"


class CalibrationPrompt(): 
    
    """Class for handling easy creation of multi point
    calibrations. Should be easy to extend to different
    types of calibrations just depending on how it is called.
    Not sure how easy it is to subclass, since all of the tkinter
    widget setup is done in __init__

    Usage:
        m = CalibrationPrompt(test type, x_axis_label, y_axis_label)
        all 3 args are strings, and will appear in dialog as
        well as the resulting excel sheet.

    Note: variable names might be legacy from initial creation
    for use in RTD temp cal, where RAW = x_axis, TC = y axis for everything.
    I think I refactored everything by now.

    To extend, start by moving initialization code into private
    subroutines which allow easier navigation and organization.
    As is, much of the __init__ code order is due to a) the order
    that I thought of it in, and b) the order of creation that
    creates a logical tab stop order. a) Presents no obstacles
    for code reuse, while b) either requires some research, or
    some really annoying re-creation of buttons.

    #Todo:
        -Lock root window size.
        -Control tab stop order.
        -Make add button not right above "_finish" button.
        -Leave more space by default so that window doesn't have to
            resize every time non-default entries are added/removed.
        -Make prettier.
        -Add checkbox for printout
            eventually might need to expand to options menu
            but no plans to expand that far.
        -Wrap
    """
    
    def __init__(self, Type, yLabel, xLabel='Raw Measure'):
        """Set up all tkinter widgets and settings"""
        
        #store arg copies for later export
        self.test_type = Type
        self.x_label = xLabel
        self.y_label = yLabel
        
        #some grid config constants
        #should move these to a better place 
        #but at least this way the class itself
        #can be copy/pasted to other files
        self.YDAT_COL = 2
        self.XDAT_COL = 1
        self.TESTTYPE_COL = 0
        self.HEADER_ROW = 3
        self.DATA_ENTRY_START_ROW = 5
        
        self.root = tk.Tk()
        self.root.resizable(width=False, height=False)
        self.frame = ttk.LabelFrame(self.root, text="Enter Info:")
        frame = self.frame
        
        self.reactor_name_header = ttk.Label(frame, text="Bioreactor Name:")
        self.ydat_header = ttk.Label(frame, text=yLabel)
        self.xdat_header = ttk.Label(frame, text=xLabel)
        self.type_header = ttk.Label(frame, text=(Type + ":"))
        
        #make action buttons now bc of resulting tab stop order 
        self.finish_button = ttk.Button(frame, text="Finish", command=self._finish)
        self.cancel_button = ttk.Button(frame, text="Cancel", command=self.CloseDialog)
        self.add_button = ttk.Button(frame, text="Add", command=self._add_temp_pt)
        
        #reactor type
        self.rsize_var = tk.StringVar(frame)
        
        #first entry must be dummy! disappears after another option is selected 
        self.rsize_menu = ttk.OptionMenu(frame, self.rsize_var, "Reactor Size", "3L", "15L", "80L", "500L")
        
        #entry for bioreactor name:
        self.reactor_name_entry = ttk.Entry(frame)
        
        #two default tc entries
        #two default raw entries
        #create in this order bc of tab stop order
        self.xdat_e0 = ttk.Entry(frame)
        self.ydat_e0 = ttk.Entry(frame)
        self.xdat_e1 = ttk.Entry(frame)
        self.ydat_e1 = ttk.Entry(frame)
        
        #spacer dummies. name fmt: dmy_[col][row]
        self.dmy_01 = ttk.Label(frame)
#         self.dmy_17 = ttk.Label(frame)
        self.dmy_30 = ttk.Label(frame, text=" " * 25)
        
        #grid all the things!
        self.frame.grid()
        self.reactor_name_header.grid(column=self.TESTTYPE_COL, row=0)
        self.type_header.grid(column=self.TESTTYPE_COL, row=2)
        self.ydat_header.grid(column=self.YDAT_COL, row=self.HEADER_ROW)
        self.xdat_header.grid(column=self.XDAT_COL, row=self.HEADER_ROW)
        
        self.reactor_name_entry.grid(column=self.XDAT_COL, row=0)
        self.xdat_e0.grid(column=self.XDAT_COL, row=self.DATA_ENTRY_START_ROW)
        self.ydat_e0.grid(column=self.YDAT_COL, row=self.DATA_ENTRY_START_ROW)
        self.xdat_e1.grid(column=self.XDAT_COL, row=(self.DATA_ENTRY_START_ROW + 1))
        self.ydat_e1.grid(column=self.YDAT_COL, row=(self.DATA_ENTRY_START_ROW + 1))

        self.add_button.grid(column=self.YDAT_COL, row=(self.DATA_ENTRY_START_ROW + 2), sticky=tk.E)        
        self.finish_button.grid(column=self.YDAT_COL, row=(self.DATA_ENTRY_START_ROW + 4), sticky=tk.W)
        self.cancel_button.grid(column=self.XDAT_COL, row=(self.DATA_ENTRY_START_ROW + 4), sticky=tk.E)
        
        self.dmy_01.grid(column=self.TESTTYPE_COL, row=1)
#         self.dmy_17.grid(column=self.XDAT_COL, row=(self.DATA_ENTRY_START_ROW+3))
        self.dmy_30.grid(column=3, row=0)
        
        self.rsize_menu.grid(column=self.YDAT_COL, row=0)

        #allows dynamic insertion/removal of entries
        self.cal_pt_list = [
                    (self.xdat_e0, self.ydat_e0),
                    (self.xdat_e1, self.ydat_e1)
                    ]
                    
        #use to solve problems with resizing later
        self.move_down_list = [
                               self.add_button, 
                               self.finish_button, 
                               self.cancel_button
                               ]
                               
        self._data = None
        self._complete = False
    
    def _add_temp_pt(self):
        """Add Temp Cal Point"""
        frame = self.frame
        
        new_xdat_e = ttk.Entry(frame)
        new_ydat_e = ttk.Entry(frame)
        
        cur_pts = len(self.cal_pt_list)
        
        new_ydat_e.grid(column=self.YDAT_COL, 
                      row=(self.DATA_ENTRY_START_ROW + cur_pts))
                      
        new_xdat_e.grid(column=self.XDAT_COL,
                       row=(self.DATA_ENTRY_START_ROW + cur_pts))
        
        self.cal_pt_list.append((new_xdat_e, new_ydat_e))
        
        new_del_btn = ttk.Button(frame, text="Delete", 
                                 command=lambda: self._del_temp_pt(new_xdat_e, 
                                                                new_ydat_e, 
                                                                new_del_btn))
        new_del_btn.grid(column=self.YDAT_COL + 1, row=(self.DATA_ENTRY_START_ROW + cur_pts))
        
        for widget in self.move_down_list:
            row = widget.grid_info()['row']
            widget.grid_configure(row=(int(row) + 1))
        
    #remove temp cal point
    def _del_temp_pt(self, xdat, ydat, dbtn):
        self.cal_pt_list.remove((xdat,ydat))
        xdat.grid_forget()
        ydat.grid_forget()
        dbtn.grid_forget()
        del xdat
        del ydat
        del dbtn
        
    #_finish and CloseDialog buttons
    def _finish(self):
        data = []

        for i, (x_data, y_data) in enumerate(self.cal_pt_list):
            try:
                data.append((float(x_data.get()), float(y_data.get())))
            except ValueError:
                print("Enter valid _data for row %d" % (i + 1))
                return
        
        r_name = self.reactor_name_entry.get()
        if not r_name:
            print("Enter a bioreactor name.")
            return
        
        rtype = self.rsize_var.get()
        if rtype == "Reactor Size":
            print("Select bioreactor size.")
            return
            
        self._data = {
                     'Name' : r_name,
                     '_data' : data,
                     'Size' : rtype,
                     'xLabel' : self.x_label,
                     'yLabel' : self.y_label,
                     'Type' : self.test_type,
                     'Printout' : False
                     }
                     
        self._complete = True
        self.root.destroy()
        
    def CloseDialog(self):
        self.root.destroy()
        raise DialogIncompleteError
        
    def Execute(self):
        self.root.mainloop()
        if not self._complete:
            print(self.rsize_var.get())
            raise DialogIncompleteError
  
    def getData(self):
        return self._data
    
    
class MultiCalPrompter():
    
    """This is the prompt that gets user info
    for what type of calibration user wants to perform.

    This functionality should (probably) be wrapped into
    CalibrationPrompt class itself, and name changed to be more descriptive.

    For now, it is functional, though doesn't natively interface
    with CalibrationPrompt class- user has to call CalibrationPrompt with info from this
    prompt."""
    
    _complete = False
    __info = None
    
    def __init__(self, *, AutoStart=True):
        
        self.root = tk.Tk()
        self.root.resizable(width=False, height=False)
        self.frame = ttk.LabelFrame(self.root, text="Enter Cal Info:")
        _r = self.root
        _f = self.frame
        
        self.run_btn = ttk.Button(_f, text="Start", command=self.EndInfoPrompt)
        self.cancel_btn = ttk.Button(_f, text="Cancel", command=self.CloseDialog)
        
        self.cal_type_entry = ttk.Entry(_f)
        self.cal_type_label = ttk.Label(_f, text="Test Name:") 
        
        self.x_entry = ttk.Entry(_f)
        self.x_entry.insert(0, "Raw Measure")
        self.x_label = ttk.Label(_f, text="X Parameter")
        
        self.y_entry = ttk.Entry(_f)
        self.y_label = ttk.Label(_f, text="Y Parameter")
        
        self.GridFrameWidgets()
        self.GridNavWidgets()
        self.GridInfoWidgets()
        
        if AutoStart == True:
            self.Execute()

    def CloseDialog(self):
        self.root.destroy()
        
    def EndInfoPrompt(self):
        """get info and destroy root"""
        
        errors = []
        
        test_type = self.cal_type_entry.get()
        if test_type == "":
            errors.append("Enter calibration type.")
        
        yLabel = self.y_entry.get()
        if yLabel == "":
            errors.append("Enter Y parameter name.")
            
        xLabel = self.x_entry.get()
        if xLabel == "":
            errors.append("Enter X Parameter name.")
        
        if errors:
            for error in errors:
                print(error)
            
            print("\n")
            return
            
        self.__info = {
                     'Type': test_type,
                     'yLabel' : yLabel,
                     'xLabel' : xLabel
                     }
                     
        self._complete = True
        self.CloseDialog()
                          
    def getData(self):
        return self.__info

    def GridNavWidgets(self):
        """Run and CloseDialog buttons"""
        self.run_btn.grid(column=1, row=2)
        self.cancel_btn.grid(column=0, row=2)
        
    def GridInfoWidgets(self):
        """Entry and Label widgets"""
        self.cal_type_entry.grid(column=0, row=1)
        self.cal_type_label.grid(column=0, row=0)
        
        self.x_entry.grid(column=1, row=1)
        self.x_label.grid(column=1, row=0) 
        
        self.y_entry.grid(column=2, row=1)
        self.y_label.grid(column=2, row=0)
        
    def GridFrameWidgets(self):
        """Any Parent Widgets"""
        self.frame.grid() 
        
    def Execute(self):
        self.root.mainloop()
        if not self._complete:
            raise DialogIncompleteError
            
    def LaunchMPC(self):
        if not self._complete:
            raise DialogIncompleteError("Error: can't launch incomplete calibration prompt.")
            
        ctxt = self.getData()
        mpc = CalibrationPrompt(**ctxt)
        try:
            mpc.execute()
            dat = mpc.getData()
        except:
            print("Error occurred running Calibration prompt")
            raise
            
        return dat
            
    @property
    def Complete(self):
        return self._complete
   
   
def setup_cal_template(range_obj, data_range, reactor_name, test_type, xlabel='', ylabel=''):
    
    """Logic to set up the excel template page
        pass range_obj param to more easily set up
        multiple templates/worksheets if needed."""
    cs = xllib.cellStr
    
    range_obj(2,2).Value = 'Reactor:'
    range_obj(2,3).Value = reactor_name
    range_obj(2,4).Value = test_type 
    range_obj(4,2).Value = xlabel
    range_obj(4,3).Value = ylabel
    
    xllib.changeBorders(AddRange=data_range)
    xllib.changeBorders(AddRange=range_obj.Range(cs(4,2) + ':' + cs(4,3)))


def PlotData(data):

    """Take _data from input _data,
    do the actual work of plotting in excel"""
    
    global xl, wb, ws, cells 

    '''Extract _data'''
    rname = data.get('Name', '')
    rtype = data.get('Size', '')
    _printout = data.get('Printout', False)
    cells(2,3).Value = rname
    cal_data = data['_data']
    data_pts = len(cal_data)
    ttype = data['Type']
    ylabel = data['yLabel']
    xlabel = data['xLabel']
    '''Setup template, minus chart'''
    
    data_range = cells.Range(cells(5,2), cells(4 + data_pts, 3))   
    setup_cal_template(cells, data_range, rname, ttype, xlabel, ylabel)

    data_range.Value = cal_data
    
    chart = xllib.createChart(ws, Top=(15 * (4.5 + data_pts)), 
                                  Left=(64 * xllib.XL_PIXEL_TO_POINT), 
                                  Height=(14.5 * 15), 
                                  Width=(64 * xllib.XL_PIXEL_TO_POINT * 7.5))
    
    try:
        chart.SeriesCollection(1).Delete()
    except:
        pass
        
    Series = chart.SeriesCollection().NewSeries()

    Series.Values = cells.Range(xllib.cellRangeStr((5,3,1,1),(4 + data_pts, 3,1,1)))
    Series.XValues = cells.Range(xllib.cellRangeStr((5,2,1,1),(4 + data_pts, 2,1,1)))
        
    xllib.formatChart(chart,
                      Legend=False,
                      ChartTitle=(rname + " " + ttype), 
                      Trendline=True,
                      xAxisTitle=xlabel,
                      yAxisTitle=ylabel)   
    
    try:
        savefolder = ''.join(rname.split(rtype))
    except:
        try:
            savefolder = ''.join(rname.split(rtype[0]))
        except:
            savefolder = rname
        
    savepath = ''.join([FUNC_TEST_FOLDER, "\\", rtype, '\\', savefolder])

    try:
        makedirs(savepath)
    except OSError:  # folder already exists? 
        pass
 
    filename = ''.join((savepath, "\\", rname, " ", data['Type']))
    
    #don't override stuff
    fudge = '' 
    if exists(filename + '.xlsx'):
        fudge = 1
        while exists(''.join((filename, str(fudge), '.xlsx'))):
            fudge += 1
    
    filename = ''.join((filename, str(fudge), ".xlsx"))
    wb.SaveAs(Filename=filename)
     
#     if printout:
#         ws.PrintOut()
#     
    print(savepath, '\n', filename)
    
    
def RtdCalMain():
    
    dlg = CalibrationPrompt(Type="Temp Cal", 
                             xLabel="Raw Measure", 
                             yLabel="Thermocouple")
    try:
        dlg.Execute()
    except DialogIncompleteError: 
        input(">>> Dialog canceled by user. Press any key to exit.")
        exit()
    except BaseException as error:
        print("Error occurred, aborting analysis.")
        print(error)
        raise
    return dlg.getData()
    
    
def CreateSpreadsheet(data):
    
    global xl, wb, ws, cells
#     xl, wb, ws, cells = xllib.xlObjs("C:\\Users\\Public\\Documents\\PBSSS\\PBS 3 RTD cal template.xlsx", visible=False)
    xl, wb, ws, cells = xllib.xlObjs()
    try:
        PlotData(data)
        print("Data plotted successfully!")
    except:
        print("Error occurred, unable to plot data.")
        with open(FUNC_TEST_FOLDER + "/bkup.txt", 'w') as f:
            for k,v in data.items():
                f.write(''.join((k, ' \'', str(v), '\'\n')))
        print("Data backed up in %s." % (FUNC_TEST_FOLDER + "/bkup.txt"))
        raise
    finally:
        xl.Visible = True
#         wb.Close()
#         xl.Quit()


def main():
    info_dlg = MultiCalPrompter(AutoStart=False)
    
    try:
        info_dlg.Execute()
        info_ctxt = info_dlg.getData()
        c = CalibrationPrompt(**info_ctxt)
        c.Execute()
    except DialogIncompleteError: 
        input(">>> Dialog canceled by user. Press enter to exit.")
        exit()
    except:
        input(">>> Error occurred. Press enter to abort analysis.")
        raise
    
    data = c.getData()
    CreateSpreadsheet(data)
    
if __name__ == "__main__":
    main()
    
