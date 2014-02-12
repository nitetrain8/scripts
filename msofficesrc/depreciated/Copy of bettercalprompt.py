"""
Created on Dec 12, 2013

@author: PBS Biotech
"""
import tkinter as tk
import tkinter.ttk as ttk
from os import makedirs
from officelib.xllib import cellRangeStr, changeBorders, \
                            formatChart, createChart, XL_PIXEL_TO_POINT, \
                            xlObjs
from officelib.olutils import getUniqueName

FUNC_TEST_FOLDER = "C:\\Users\\Public\Documents\\PBSSS\\Functional Testing"


class DialogIncomplete(Exception):
    pass
    
    
'''Helper classes'''
    
    
class SimplePrompt():
    """ Simple helper class to open a window
    with two buttons (ok and cancel), and a text entry

    @param: display_text - the text to display on the labelframe.

    @return: string entered by user, if dialog completed with exit status
            0.

    """
    
    def ask(self, display_text='SimplePrompt'):
        
        self.display_text = display_text
        
        root = tk.Toplevel()
        self.root = root
        
        frame = ttk.LabelFrame(root, text=self.display_text)
        
        ok_btn = ttk.Button(frame, text="Ok", command=self.ok_action)
        cancel_btn = ttk.Button(frame, text="Cancel", command=self.cancel_action)
        
        text_var = tk.StringVar()
        self.text_var = text_var
        
        text_entry = tk.Entry(frame, width=40, textvariable=text_var)
        
        frame.bind_all("<Key>", self.key_event_handler)
        
        text_entry.grid(columnspan=4, row=0)
        ok_btn.grid(column=2, row=1, sticky=tk.W)
        cancel_btn.grid(column=1, row=1, sticky=tk.E)
        
        text_entry.focus()
        frame.grid()
        root.grab_set()
        self._return_text = None
        
        root.wait_window(self.root)
        
        return self._return_text
        
    def key_event_handler(self, event):
        
        ENTER = 13
        ESC = 27
        keycode = event.keycode
        
        if keycode == ENTER:
            self.ok_action()
            
        elif keycode == ESC:
            self.cancel_action()
        
    def ok_action(self):    
        text = self.text_var.get()
        if text:
            self._return_text = text
            self._complete = True
            self.root.destroy()
        else:
            self.root.bell()
    
    def cancel_action(self):
        self.root.destroy()
        
        
class SimpleCheckBox(ttk.Checkbutton):
    """Simple helper class to make working with a checkbox easier.

    Identical to ttk.Checkbutton, but auto-inits its variable
    if necessary, and provides direct access to its var with get()
    set() select() setState() toggle() etc methods. Also provides
    a direct trace method.

    """
    
    def __init__(self, *args, **kwargs):

        self.var = kwargs.get('variable', tk.IntVar())
        kwargs['variable'] = self.var
        super(SimpleCheckBox, self).__init__(*args, **kwargs)

    def get(self):
        return self.var.get()
        
    def getState(self):
        return self.var.get()
        
    def setState(self, state):
        self.var.set(state)
        
    def select(self):
        self.var.set(1)
        
    def toggle(self):
        self.var.set(1 - self.var.get())
        
    def connectTrace(self, cb):
        self.var.trace('w', cb)


def _MPC_load_cfg():
    
    # external cfg file?
    # param of class?
    
    testtype_col = 0
    xdat_col = testtype_col + 1
    ydat_col = xdat_col + 1
    header_row = 2
    default_entry_rows = 5
    data_entry_start_row = header_row + 3 
    reactor_sizes = ['3L', '15L', '80L', '500L']
    custom_axis = 'Custom...'
    default_xaxis = "Raw Measure"
    default_yaxis = "Temperature"
    default_size = 'Reactor Size'
    yaxes = ['Pressure', 'Temperature', 'pH', 'DO', custom_axis]
    xaxes = ['Raw Measure', custom_axis]
    frame_column_span = 8
    add_btn_col = ydat_col + 1
    cancel_btn_col = 3
    run_btn_col = cancel_btn_col + 1
    checkbox_col = 3
    checkbox_start_row = 0
    default_save_folder = FUNC_TEST_FOLDER
    nav_button_row = data_entry_start_row + 4 + default_entry_rows
    
    cfg = {
            'YDAT_COL' : ydat_col,
            'XDAT_COL' : xdat_col,
            'TESTTYPE_COL' : testtype_col,
            'HEADER_ROW' : header_row,
            'DEFAULT_ENTRY_ROWS' : default_entry_rows,
            'DATA_ENTRY_START_ROW' : data_entry_start_row,
            'RSIZES' : reactor_sizes,
            'CUSTOM_AXIS_INDICATOR' : custom_axis,
            'DEFAULT_XAXIS' : default_xaxis,
            'DEFAULT_YAXIS' : default_yaxis,
            'DEFAULT_SIZE' : default_size,
            'YAXES' : yaxes,
            'XAXES' : xaxes,
            'FRAME_COLUMN_SPAN' : frame_column_span,
            'ADD_BTN_COL' : add_btn_col,
            'CANCEL_BTN_COL' : cancel_btn_col,
            'RUN_BTN_COL' : run_btn_col,
            'CHECKBOX_COL' : checkbox_col,
            'CHECKBOX_START_ROW' : checkbox_start_row,
            'DEFAULT_SAVE_FOLDER' : default_save_folder,
            'NAV_BUTTON_ROW' : nav_button_row
        }
    
    return cfg


class CalibrationPrompt(): 
    
    """Class for handling easy creation of multi point
    calibrations.

    Usage:
        m = CalibrationPrompt()

    Much initialization code has been moved into subroutines for
    better organization, but everything will break if stuff is
    moved around too much. It makes it easier to find stuff,
    at least.

    To significantly change UI, its probably worthwhile to start by
    inlining all of the setup subroutines.

    #Todo:
        -Control tab stop order.
        -Make prettier.

    update 1/14/2014:
        misc cleanup w/ pep8.py, removing old commented-out code
        enforce more consistent function naming:

        __funcname, __func_name, __func_name_ -> the more underscores, the more
                                                 wtf if you try to change these

        _func_name - model function

        funcName - programming interface (controller) /view function

        added ability to enter custom axis name.

    """
    _complete = False

    #get/store cfg options 

    _cfg = _MPC_load_cfg()
    
    def __init__(self):
        """Set up all tkinter widgets and settings"""
        
        self.root = tk.Tk()
        self.root.resizable(width=False, height=False)
        self.frame = ttk.LabelFrame(self.root, text="Enter Info:")

        frame = self.frame
        root = self.root
        
        self._setup_action_buttons(frame, root)
        
        self._setup_label_menus(frame)
        
        self._setup_field_labels(frame)
        
        self._setup_entry_fields(frame)
                            
        #checkboxes
        self.xl_persist_ckbx = SimpleCheckBox(frame, text="Leave Excel Open")
        self.printout_ckbx = SimpleCheckBox(frame, text="Print out when done")
        self.xl_persist_ckbx.select()
        
        self._grid_all_the_things()
        
        self._data = None
        self._complete = False

    def _grid_all_the_things(self):
        
        """Unpack constants from config to make code slightly more readable.
        also slightly less hacky than locals().update(self._cfg)

        """
        cfg = self._cfg
        
        YDAT_COL = cfg['YDAT_COL']
        XDAT_COL = cfg['XDAT_COL']
        TESTTYPE_COL = cfg['TESTTYPE_COL']
        HEADER_ROW = cfg['HEADER_ROW']
        DATA_ENTRY_START_ROW = cfg['DATA_ENTRY_START_ROW']
        FRAME_COLUMN_SPAN = cfg['FRAME_COLUMN_SPAN']        
        ADD_BTN_COL = cfg['ADD_BTN_COL']
        CANCEL_BTN_COL = cfg['CANCEL_BTN_COL']
        RUN_BTN_COL = cfg['RUN_BTN_COL']
        CHECKBOX_START_ROW = cfg['CHECKBOX_START_ROW']
        CHECKBOX_COL = cfg['CHECKBOX_COL']
        NAV_BUTTON_ROW = cfg['NAV_BUTTON_ROW']

        #grid all the things!
        self.frame.grid(columnspan=FRAME_COLUMN_SPAN)
        
        self.br_name_header.grid(column=TESTTYPE_COL, row=0)
        self.type_header.grid(column=TESTTYPE_COL, row=2)
        self.ydat_header.grid(column=YDAT_COL, row=HEADER_ROW)
        self.xdat_header.grid(column=XDAT_COL, row=HEADER_ROW)
        
        self.test_type_entry.grid(column=TESTTYPE_COL, row=3)
        self.reactor_name_entry.grid(column=XDAT_COL, row=0)
        
        for row, (x_entry, y_entry, dummy) in enumerate(self.cal_pt_list):
            x_entry.grid(column=XDAT_COL, row=(DATA_ENTRY_START_ROW + row))
            x_entry.bind("<Key>", self._check_number_input)
            
            y_entry.grid(column=YDAT_COL, row=(DATA_ENTRY_START_ROW + row))
            y_entry.bind("<Key>", self._check_number_input)
        
        #This is unreadable. Sorry.
        self.add_button.grid(column=ADD_BTN_COL, 
                             row=DATA_ENTRY_START_ROW, 
                             sticky=tk.W)
                             
        self.finish_button.grid(column=RUN_BTN_COL, 
                                row=(NAV_BUTTON_ROW), 
                                sticky=tk.W)
                                
        self.cancel_button.grid(column=CANCEL_BTN_COL, 
                                row=(NAV_BUTTON_ROW), 
                                sticky=tk.E)
                                
        self.xl_persist_ckbx.grid(column=CHECKBOX_COL, 
                                    row=CHECKBOX_START_ROW, 
                                    sticky=tk.W)
                                    
        self.printout_ckbx.grid(column=CHECKBOX_COL, 
                                row=CHECKBOX_START_ROW + 1, 
                                sticky=tk.W)
                                
        self.rsize_menu.grid(column=YDAT_COL, row=0)
        self.yaxis_menu.grid(column=YDAT_COL, row=HEADER_ROW + 1, sticky=(tk.E, tk.W))
        self.xaxis_menu.grid(column=XDAT_COL, row=HEADER_ROW + 1, sticky=(tk.E, tk.W))

    def _setup_entry_fields(self, frame):
        """ Create default # of rows of x/y _data point pairs
    cal_pt_list is a list of tuples: (x_entry, y_entry, delete_button)
    none is placeholder for delete button widget, since these
    defaults won't be deleted.

    vcmd = tuple of validation command + '%' modifier args.

    ref - http://www.tcl.tk/man/tcl8.5/TkCmd/entry.htm#M-validate
          http://stackoverflow.com/questions/4140437/python-tkinter-interactively-validating-entry-widget-content/4140988#4140988

    """
        rows = self._cfg['DEFAULT_ENTRY_ROWS']
        
        self.check_input_vcmd = self.root.register(self._check_number_input), '%P'
        entry_kw = {'validate':"key", 'validatecommand':self.check_input_vcmd}
        
        self.cal_pt_list = [(ttk.Entry(frame, **entry_kw), 
                            ttk.Entry(frame, **entry_kw), None) for 
                            _ in range(rows)]
                            
        #entries for name, test type
        self.reactor_name_entry = ttk.Entry(frame)
        self.test_type_entry = ttk.Entry(frame)

    def _setup_field_labels(self, frame):
        self.br_name_header = ttk.Label(frame, text="Bioreactor Name:")
        self.ydat_header = ttk.Label(frame, text="Y Axis:")
        self.xdat_header = ttk.Label(frame, text="X Axis:")
        self.type_header = ttk.Label(frame, text="Test Type:")

    def _setup_label_menus(self, master):
        
        cfg = self._cfg
        RSIZES = cfg['RSIZES']
        YAXES = cfg['YAXES']
        XAXES = cfg['XAXES']
        DEFAULT_XAXIS = cfg['DEFAULT_XAXIS']
        DEFAULT_YAXIS = cfg['DEFAULT_YAXIS']
        DEFAULT_SIZE = cfg['DEFAULT_SIZE']
        
        #stringvars for various menus
        self.rsize_var = tk.StringVar(master)  # reactor size
        self.yaxis_var = tk.StringVar(master)  # y axis name
        self.xaxis_var = tk.StringVar(master)  # x axis name
        self.xaxis_var.set(DEFAULT_XAXIS)
        self.yaxis_var.set(DEFAULT_YAXIS)
        #said menus
        #first entry must be dummy! disappears after another option is selected
        self.rsize_menu = ttk.OptionMenu(master, 
                                        self.rsize_var, 
                                        DEFAULT_SIZE, *
                                        RSIZES)
                                        
        self.yaxis_menu = ttk.OptionMenu(master, 
                                        self.yaxis_var, 
                                        DEFAULT_YAXIS, *
                                        YAXES, 
                                        command=self.y_axis_menu_changed)
                                        
        self.xaxis_menu = ttk.OptionMenu(master, 
                                        self.xaxis_var, 
                                        DEFAULT_XAXIS, *
                                        XAXES, 
                                        command=self.x_axis_menu_changed)

    def _setup_action_buttons(self, frame, root):
        
        """Setup action buttons.

        @param: frame- the frame in which to grid the add button
        @param: root- the frame in which to grid the nav buttons

        """
        
        #make action buttons now bc of resulting tab stop order
        self.finish_button = ttk.Button(root, text="Finish", command=self._finish)
        self.cancel_button = ttk.Button(root, text="Cancel", command=self.CloseDialog)
        self.add_button = ttk.Button(frame, text="Add Point", command=self._add_temp_pt)
        
        tk_btn_class = self.cancel_button.winfo_class()
        self.frame.bind_class(tk_btn_class, "<Return>", self._invoke_command)

    def y_axis_menu_changed(self, selection):
        
        """Event listener on OptionMenu change.

        @param: selection- the new selection value (string)

        """
        if selection != self._cfg['CUSTOM_AXIS_INDICATOR']:
            return
            
        prompt = SimplePrompt()
        result = prompt.ask("Enter y-axis name:") 
        
        if not result:
            return
            
        self.yaxis_var.set(result)
        
        new_menu_list = [result] + self._cfg['YAXES']
        
        self.yaxis_menu.set_menu(result, *new_menu_list)
        self.yaxis_menu['menu'].invoke(0)

    def x_axis_menu_changed(self, selection):
        
        """Event listener on OptionMenu change.

        @param: selection- the new selection value (string)

        """
        
        if selection != self._cfg['CUSTOM_AXIS_INDICATOR']:
            return
            
        prompt = SimplePrompt()
        result = prompt.ask("Enter x-axis name:") 
        
        if not result:
            return
            
        self.xaxis_var.set(result)
        self.xaxis_menu.set_menu(result, *([result] + self._cfg['XAXES']))
        self.xaxis_menu['menu'].invoke(0)

    def _add_temp_pt(self):

        """Add Temp Cal Point"""
        frame = self.frame
        cfg = self._cfg
        new_x_entry = ttk.Entry(frame)
        new_y_entry = ttk.Entry(frame)
        current_points = len(self.cal_pt_list)

        new_row = cfg['DATA_ENTRY_START_ROW'] + current_points
        x_column = cfg['XDAT_COL']
        y_column = cfg['YDAT_COL']

        new_y_entry.grid(column=y_column, row=new_row) 
        new_x_entry.grid(column=x_column, row=new_row)
                       
        new_del_btn = ttk.Button(frame, text="Delete", 
                                 command=lambda: self._del_temp_pt((new_x_entry, 
                                                                new_y_entry, 
                                                                new_del_btn)))
        
        self.cal_pt_list.append((new_x_entry, new_y_entry, new_del_btn))
                                                                        
        new_del_btn.grid(column=cfg['YDAT_COL'] + 1, 
                         row=(cfg['DATA_ENTRY_START_ROW'] + current_points),
                         sticky=tk.W)
        
    def _del_temp_pt(self, data_point_tuple):
        
        """Delete a temp point by looking up the index in the point
        list by value. This uses a list with O(n) lookup, because the
        only other alternative is an OrderedDict or linked-list-dict-thingy

        @param: data_point_tuple - tuple of xdata_entry, ydata_entry,
                                    delete_button created in _add_temp_pt.
                                    Called automatically by lambda callback.

        Should/can never be called directly.

        """
        
        i = self.cal_pt_list.index(data_point_tuple)
        
        for (x_col, y_col, del_btn) in self.cal_pt_list[i + 1:]:
            new_row = int(x_col.grid_info()['row']) - 1
            x_col.grid_configure(row=new_row)
            y_col.grid_configure(row=new_row)
            del_btn.grid_configure(row=new_row)
            
        data_point_tuple[0].grid_forget()
        data_point_tuple[1].grid_forget()
        data_point_tuple[2].grid_forget()
        
        self.cal_pt_list.pop(i)
        
    def _invoke_command(self, event):
        
        """Event handler for .bind("<Return>") events.
        @param: event- the event generated, sent to the handler
        """
        
        event.widget.invoke()
        
    def _check_number_input(self, new_value):
        """Event handler for verifying proper entry into data
        point boxes. Verify by attempting to convert value to float.

        @param: new_value- the value that would appear in the box if
                            validation were to return True.
        """
        try:
            float(new_value)
            return True
        except:
            return False
        
    def _finish(self):
        """Finish and close dialog buttons. This function does
        checking to be sure that data is good, iterating through all
        the things and appending to a list of errors. If errors, print
        errors, return. Otherwise, shut down the dialog and export data.

        """
        errors = []
        data = []
        pts = 0
        
        '''Need to use external counter so it fails to increment on
        ValueError. Throw error for anything that would result in
        failure to convert to float.'''
                
        for xdat, ydat, dummy in self.cal_pt_list:
            try:
                data.append((float(xdat.get()), float(ydat.get())))
                pts += 1
            except ValueError:
                pass

        if pts < 2:
            errors.append("Need at least two valid points.")
        
        r_name = self.reactor_name_entry.get()
        if not r_name:
            errors.append("Enter a bioreactor name.")
        
        rtype = self.rsize_var.get()
        if rtype == self._cfg['DEFAULT_SIZE']:
            errors.append("Select bioreactor size.")
            
        x_label = self.xaxis_var.get()
        if x_label == "":
            errors.append("Select an X axis label.")
            
        y_label = self.yaxis_var.get()
        if y_label == "":
            errors.append("Select an Y axis label.") 
            
        test_type = self.test_type_entry.get()
        if test_type == "":
            errors.append("Enter the test name.") 
            
        if errors:
            msg = ''.join((
                          '\nCan\'t finish yet, errors found:',
                          '\n   ',
                          '\n   '.join(errors),
                          '\n\n'
                          ))
            print(msg)
            
        else: 
            self._data = {
                         'Name' : r_name,
                         'Data' : data,
                         'Size' : rtype,
                         'xLabel' : x_label,
                         'yLabel' : y_label,
                         'Type' : test_type,
                         'Printout' : self.printout_ckbx.get(),
                         'Persist' : self.xl_persist_ckbx.get(), 
                         'SaveFolder' : FUNC_TEST_FOLDER  # not yet implemented
                         }
                         
            self._complete = True
            self.root.destroy()
        
    def CloseDialog(self):
        """Close dialog by destroying root."""
        
        self.root.destroy()
        
    def Execute(self):
        """Call this to start the dialog"""
        self.root.mainloop()
        if not self._complete:
            raise DialogIncomplete
  
    def getData(self):
        return self._data
    
    @property
    def Data(self):
        return self._data
    
    data = Data  
    
    @property
    def isComplete(self):
        return self._complete
        

def SetupCalTemplate(range_obj, data_points, reactor_name='', test_type='', xlabel='', ylabel=''):
    
    """Logic to set up the excel template page
        pass range_obj param to more easily set up
        multiple templates/worksheets if needed.

    @param: range_obj - the base range object (eg, ws.Cells) to insert into.
                        Offsets will be offset relative to top left range object
                        cell

    @param: data_points  - the # of _data points to be plotted
                            will be used to calculate range to change borders

    @param: reactor name- the name to go in reactor name cell/chart title

    @param test_type- the name to put in test type cell/chart title

    @param xlabel- the name of the x-axis

    @param ylabel- the name of the y-axis

    """
    
    range_obj(2,2).Value = 'Reactor:'
    range_obj(2,3).Value = reactor_name
    range_obj(2,4).Value = test_type 
    range_obj(4,2).Value = xlabel
    range_obj(4,3).Value = ylabel
    
    border_range = range_obj.Range(range_obj(5,2), 
                                   range_obj(5 + data_points, 3))    
    
    changeBorders(AddRange=border_range)
    

def PlotData(xlctxt, data):

    """Take _data from input _data,
    do the actual work of plotting in excel

    @param: xlctxt- context object (tuple) containing
                    references to the relevant Excel
                    application, workbook, worksheet,
                    and worksheet cells objects.

    @param: data- data object from successful CalibrationPrompt dialog

    """
    
    _xl, wb, ws, cells = xlctxt

    # Extract _data with default get values 
    reactor_name = data.get('Name', '')
    model_size = data.get('Size', '')
    printout = data.get('Printout', False)
    test_type = data.get('Type', '')
    ylabel = data.get('yLabel', 'y Value')
    xlabel = data.get('xLabel', 'x Value')
    save_folder_base = data.get('SaveFolder', FUNC_TEST_FOLDER)
    
    cal_data = data['Data']
    data_points = len(cal_data)
    
    # Setup template, minus chart
    
    SetupCalTemplate(cells, 
                     data_points, 
                     reactor_name, 
                     test_type, 
                     xlabel, 
                     ylabel)

    cell_range = cells.Range
    
    x_col = 2
    y_col = 3
    start_row = 5
    end_row = 4 + data_points 
    abs_ref = 1  # absolute address eg $A1
    
    # Address strings
    
    y_range = cellRangeStr(
                             (start_row, y_col, abs_ref, abs_ref), 
                             (end_row, y_col, abs_ref, abs_ref))
                             
    x_range = cellRangeStr(
                             (start_row, x_col, abs_ref, abs_ref), 
                             (end_row, x_col, abs_ref, abs_ref))
                             
    data_range = ':'.join((
                           x_range, 
                           y_range))
                             
    cell_range(data_range).Value = cal_data
    
    chart = createChart(ws, 
                        Top=(15 * (4.5 + data_points)),  # sizes in pixels
                        Left=(64 * XL_PIXEL_TO_POINT), 
                        Height=(14.5 * 15), 
                        Width=(64 * XL_PIXEL_TO_POINT * 7.5))

    try:
        chart.SeriesCollection(1).Delete()  # sometimes xl adds a series for no reason
    except:
        pass
        
    Series = chart.SeriesCollection().NewSeries()
    Series.Values = cell_range(y_range)
    Series.XValues = cell_range(x_range)
        
    formatChart(chart,
                  Legend=False,
                  ChartTitle=(reactor_name + " " + test_type), 
                  Trendline=True,
                  xAxisTitle=xlabel,
                  yAxisTitle=ylabel)
        
    save_path = ''.join((save_folder_base, 
                        "\\", 
                        model_size, 
                        "\\", 
                        reactor_name))

    try:
        makedirs(save_path)
    except OSError:
        pass

    filename = ''.join((save_path,
                             "\\",
                             reactor_name,
                             " ",
                             data['Type'],
                             '.xlsx'
                             ))

    filename = getUniqueName(filename)

    print(filename)
    wb.SaveAs(Filename=filename)

    if printout:
#         ws.PrintOut()
        print("Printout!")  # debug placeholder
 
    print(save_path, '\n', filename)
    
    
def CreateSpreadsheet(data):
    
    xl, wb, ws, cells = xlObjs("C:\\Users\\Public\\Documents\\PBSSS\\PBS 3 RTD cal template.xlsx", visible=False)
    xlctxt = (xl, wb, ws, cells)
    try:
        PlotData(xlctxt, data)
    finally:
        xl.Visible = data['Persist']
        wb.Close()
        xl.Quit()


# def main():
#     info_dlg = CalibrationPrompt(AutoStart=False)
#     
#     try:
#         info_dlg.Execute()
#         info_ctxt = info_dlg.getData()
#         c = CalibrationPrompt(**info_ctxt)
#         c.Execute()
#     except DialogIncomplete: 
#         input(">>> Dialog canceled by user. Press enter to exit.")
#         exit()
#     except:
# #         input(">>> Error occurred. Press enter to abort analysis.")
# #         raise
#     
#     data = c.getData()
#     CreateSpreadsheet(data)
    
if __name__ == "__main__":

    m = CalibrationPrompt()
    
    try:
        m.Execute()
    except DialogIncomplete:
        pass
    else:
        for k,v in m.Data.items():
            print(k,v)
