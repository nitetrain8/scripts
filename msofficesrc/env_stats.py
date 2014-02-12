"""
Created on Oct 1, 2013

@author: PBS Biotech
"""

from officelib.xllib import *
from officelib.pbslib import *
def main(): 
    import sys

    import time
    
    client = win32com.client
    
    target_path = "C:\\Users\\Public\\Documents\\PBSSS\\Miscellaneous test\\PBS 3 Environment Heater Response\\"
    target = "PBS 3 env heat response.xlsx"
    tmp_save = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MS Office\\"
    
    
    wb = xlbook(target_path + target)
    excel = wb.Parent
    batch_sheet = wb.Worksheets.Item("Batch Data")
    Cells = batch_sheet.Cells
    try:
        daily_sheet = wb.Worksheets.Item("Daily Heat & PV")
    except:
        daily_sheet = wb.Worksheets.Add()
        daily_sheet.Name = "Daily Heat & PV"
    
    wb.Worksheets(1).Select()
    
    
    
    
    def get_data(reactor_name):
        cells = Cells 
        sheet = batch_sheet
        xlapp = excel
        
        '''Scan for section with correct bioreactor 
        '''
        data_start = cells.Find(What=reactor_name, After=cells(1,1))
        data_start_col = data_start.Column
            
        
        '''Find time of day column
        '''
        heat_tod_range = cells.Find(What="Time of Day", After=cells(1,data_start.Column), SearchOrder=xlByColumns) 
        heat_tod_col = heat_tod_range.Column
        
        '''find Heat Duty column
        '''
        heat_range = cells.Find(What="Heat Duty (%)", After=cells(1,data_start.Column), SearchOrder=xlByColumns)
        heat_col = heat_range.Column
        
        
        '''find time of day col for temp PV
        '''
        
        temp_tod_range = cells.Find(What="Time of Day", After=cells(1,heat_col), SearchOrder=xlByColumns)
        temp_tod_col = temp_tod_range.Column
        
        '''find temp PV column
        '''
        temp_range = cells.Find(What="TempPV(C)", After = cells(1,temp_tod_col), SearchOrder=xlByColumns)
        temp_col = temp_range.Column
        
        
        '''Build Naive pairing of days from heat duty and temp pv cols
        '''
        
        '''Scan Heat Time of Day column for each day
        '''
        end_row = cells(1,heat_tod_col).End(xlDown).Row
        heat_data = [x[0]-int(x[0]) for x in (sheet.Range(cells(2, heat_tod_col), cells(end_row, heat_tod_col)).Value)]
        
        heat_daylist = []
        
        data_len = len(heat_data)
        heat_data.append(0)
        
        
        '''daylist for heat data
        '''
        i = 0
        while i < data_len:
            day_start = i
           
            while heat_data[i+1] >= heat_data[i]:
                i += 1 
            
            day_end = i
            i += 1
            heat_daylist.append((day_start+2, day_end+2))
           
            
        '''now scan temp's ToD column
        '''
        end_row = cells(1,temp_tod_col).End(xlDown).Row
        temp_data = [x[0] - int(x[0]) for x in sheet.Range(cells(2, temp_tod_col), cells(end_row, temp_tod_col)).Value]
       
    #     print("temp tod col: %d" % temp_tod_col)
       
        temp_daylist = []
        data_len = len(temp_data) 
        temp_data.append(0)
        
        i = 0
        while i < data_len:
            day_start = i
           
            while temp_data[i+1] >= temp_data[i]:
                i += 1 
            
            day_end = i
            i += 1
            temp_daylist.append((day_start+2, day_end+2))
        
    #     print("temp_daylist: ", temp_daylist)
    #     print("len temp_daylist: ", len(temp_daylist))
    #     
    #     print("heat_daylist: ", heat_daylist)
    #     print("len heat daylist", len(heat_daylist))
    #         
        
        days = len(temp_daylist) if len(temp_daylist) < len(heat_daylist) else len(heat_daylist)
        
        charts = daily_sheet.ChartObjects().Count
        for i in range(days):
     
            print("Now preparing chart %d..." % (i + 1))
            
            temp_day_start, temp_day_end = temp_daylist[i]
            heat_day_start, heat_day_end = heat_daylist[i]
            
            charts += 1
            width = 390
            height = 241
            left_pos = 32 + (charts % 4) * (width + 20) 
            top_pos = 15 + (charts // 4) * (height + 20) 
            
            range_sheet_string = "\'%s\'!" % sheet.Name
            chart = daily_sheet.Shapes.AddChart(xlXYScatterLines, left_pos, top_pos, width, height).Chart
    #         chart = xlapp.ActiveChart
    
    
            #get first series if it was auto added, otherwise create one
            try:
                temp_series = chart.SeriesCollection(1)
            except:
                chart.SeriesCollection().NewSeries()
                temp_series = chart.SeriesCollection(1)
                
            #delete any series beyond 2
            for series in xlrange(3, chart.SeriesCollection().Count):
                chart.SeriesCollection(series).Delete()
                
            temp_series.XValues = "{}{}:{}".format(
                                                   range_sheet_string,
                                                   cellstr(temp_day_start, temp_tod_col,1,1),
                                                   cellstr(temp_day_end, temp_tod_col,1,1),
                                                   )
                                                   
            temp_series.Values = "{}{}:{}".format(
                                                  range_sheet_string,
                                                  cellstr(temp_day_start, temp_col,1,1),
                                                  cellstr(temp_day_end, temp_col,1,1)
                                                  )
                                                 
            
            temp_series.Name = "Temp PV"
            
            '''Excel is funny about automatically giving you chart series
            (or not) when creating a new chart. Lets make sure we get access
            to the correct chart series...
            '''
            try:
                heat_series = chart.SeriesCollection(2)
            except:
                chart.SeriesCollection().NewSeries()
                heat_series = chart.SeriesCollection(2)
                
            
            
            heat_series.Name = "Heat Duty (%)"
            heat_series.XValues = "={}{}:{}".format(
                                                    range_sheet_string,
                                                    cellstr(heat_day_start, heat_tod_col, 1, 1),
                                                    cellstr(heat_day_end, heat_tod_col, 1, 1)
                                                    )
            heat_series.Values = "={}{}:{}".format(
                                                   range_sheet_string,
                                                   cellstr(heat_day_start, heat_col, 1, 1),
                                                   cellstr(heat_day_end, heat_col, 1, 1)
                                                   )
            heat_series.AxisGroup = 2
            
            
            
            chart.HasTitle = True
            chart.ChartTitle.Text = "{} day {} Heat Duty and Temp PV".format(reactor_name, i + 1)
    
            heat_series.AxisGroup = 2
            primary = chart.Axes(AxisGroup=xlPrimary)
            x_axis = primary(1)
            y_axis = primary(2)
            y2_axis = chart.Axes(xlValue, AxisGroup=xlSecondary)
            
            x_axis.HasTitle = True
            y_axis.HasTitle = True
            y2_axis.HasTitle = True
            
            x_axis.AxisTitle.Text = "Time of Day By Hour"
            y_axis.AxisTitle.Text = "TempPV (deg C)"
            y2_axis.AxisTitle.Text = "Heat Duty (%)"
            
            heat_series.MarkerSize = 2
            temp_series.MarkerSize = 2
            
            x_min_scale = x_axis.MinimumScale
            x_axis.MaximumScale = int(x_min_scale) + 2
            x_axis.MinimumScale = int(x_min_scale) + 1
            
            chart.PlotArea.Width = 250
            
            print("Success! Chart %d plotted." % (i+1))
    
            
    
    def clear_charts(sheet):
        try:
            sheet.ChartObjects().Delete()
        except:
            pass
            
    # bioreactor = "PBS 3 Hanwha I
    
    
    # clear_charts(daily_sheet)
    # 
    # get_data("PBS 3 Hanwha I")
    # get_data("PBS 3 Demo I")
    
    excel = None
    
