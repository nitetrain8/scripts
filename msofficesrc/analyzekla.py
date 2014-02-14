"""
Created on Oct 28, 2013

@author: PBS Biotech
"""
from officelib import *
from tkinter.filedialog import askopenfilenames
from officelib.const import xlToRight, xlByRows, xlDown, xlXYScatterLines, xlPrimary
from officelib.xllib.xlcom import prompt_files, xlObjs

debug_files = [
               "C:/Users/PBS Biotech/Documents/Personal/source/KLA Testing/raw batch files/kla id22 60mLPM.csv",
                "C:/Users/PBS Biotech/Documents/Personal/source/KLA Testing/raw batch files/KLA id22 500mlpm.csv",
                "C:/Users/PBS Biotech/Documents/Personal/source/KLA Testing/raw batch files/KLA ID23 0.153 LPM 500 mLPM.csv",
                "C:/Users/PBS Biotech/Documents/Personal/source/KLA Testing/raw batch files/kla ID23 60mLPM.csv"

                ]

debug_file = debug_files[0]
# raw_file = debug_file





def smooth_data(time_data):
    """smooth out time data so that there are no
    issues with multiple timestamps having exact same time"""
    
    i = 0
    while i < len(time_data):
        current_index = i
        points_to_smooth = 0
        
        try: 
            start_time = time_data[current_index]
            while start_time == time_data[i+1]:
                points_to_smooth += 1
                i += 1
        
        except IndexError: 
            del time_data[current_index + 1:]
            
        else:
            if points_to_smooth:
                end_time = time_data[i + 1]
                group_time_diff = end_time - start_time
                for time_index in range(current_index + 1, i + 1):
                    time_data[time_index] = start_time + (group_time_diff/(points_to_smooth + 1)) * (time_index - (current_index))
            
        i += 1
    
    

def build_deriv_list(times,values):
    """I could have 1-lined this with an elaborate
    list comprehension but this is more readable"""
    
    def diff(slice):
        return (slice[-1] - slice[0])
        
    def deriv(start, stop):
        #stop + 1 includes the stop index for easier math
        return diff(values[start:stop+1])/diff(times[start:stop+1])
    
    
    #0 for dummy values- deriv doesn't calc for first and last item in list
    #None should throw error if math is done on it, to alert to poor pointer arithmetic
    dlist = [None]
    dlist.extend([deriv(i-1, i+1) for i in range(1, len(values)-1)])
    dlist.append(None)
    
    return dlist
    
def make_quick_chart(ws):
    
    def insert_quick_time_col(x_data_col):
        ws.Columns(x_data_col).Insert(Shift=xlToRight)
        x_data = [x[0] for x in cells.Range(cells(2, x_data_col - 1), cells(end_data_row, x_data_col - 1)).Value2]
        smooth_data(x_data)
        cells.Range(cells(2, x_data_col), cells(len(x_data) + 1, x_data_col)).Value2 = [[(i - x_data[0])*24] for i in x_data]
        ws.Columns(x_data_col).NumberFormat = "0.00"
    
    
    cells = ws.Cells
    DO_data_start = cells.Find(What="DOPV(%)", After=cells(1,1), SearchOrder=xlByRows)
    x_data_col = DO_data_start.Column + 1
    y_data_col = x_data_col + 1
    end_data_row = DO_data_start.End(xlDown).Row

    insert_quick_time_col(x_data_col)
    
    end_data_row = cells(2, DO_data_start.Column + 1).End(xlDown).Row
    
    chart_count = ws.ChartObjects().Charts().Count
    chartpadx = 20
    chartpady = 20
    chartw = 400
    charth = 250
    chartx = 50 * x_data_col + (chartw + chartpadx) * (chart_count % 2)
    charty = 20 + (chartpady + charth) * chart_count // 2
    
    chart = ws.Shapes.AddChart(xlXYScatterLines, 50 * x_data_col, 20, 400, 250).Chart
    chart.SetSourceData(cells.Range(cells(2, x_data_col), cells(end_data_row, y_data_col)))
    
    axes = chart.Axes(AxisGroup=xlPrimary)
    x_axis = axes(1)
    y_axis = axes(2)

    from officelib.xllib.xlcom import FormatChart

    FormatChart(chart, None, "KLA", "Time(hours)", "DO PV (%)", True)
    

raw_file = prompt_files()[0]
xl, wb, ws, cells = xlObjs(raw_file)

from officelib.xllib.xlcom import HiddenXl

with HiddenXl(xl):
    make_quick_chart(ws)







