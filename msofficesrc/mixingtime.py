"""
Created on Nov 7, 2013

@author: PBS Biotech
"""

from officelib import xllib
from officelib.pbslib.proxies import BatchFile  # @UnresolvedImport
from itertools import zip_longest

class InvalidTestError(Exception):
    pass


def run_mixing_analysis(wb, batch_file):
    """main function for all analysis stuff

    Todo: "index" and "i" variables are vague and should be
    renamed to something useful
    """
    
    #this will be what the function returns
    #will contain all important results from 
    #individual file analysis
    filename = xllib.getFilename(batch_file)
    results = {'raw_file' : filename,
               't95' : None
                } 
    
    if not wb.Worksheets.Count:
        wb.Worksheets.Add()
    ws = wb.Worksheets(1)
    cells = ws.Cells
    
    #get data in nice formats
    raw_data = pbslib.ez_get_nice_data(batch_file)
    data = pbslib.dictify_nice_data(raw_data) 
    
    #Find index of first occurence of 1000 in PV col, find timestamp @ that index in Time col
    logger_col_header = "LoggerMaxLogInterval(ms)"
    start_time = data[logger_col_header]['Time'][data[logger_col_header]['PV'].index(1000)]
    mixing_col_header = guess_mixing_col_header(data)
    
    #pointers to relevant mixing time data
    mixing_data = data[mixing_col_header]
    mixing_time_data = mixing_data['Time']
    mixing_PV_data = mixing_data['PV']
    
    #get test start time
    for index in range(len(mixing_time_data)):
        timestamp = mixing_time_data[index]
        if timestamp >= start_time:
            break
    else:
        
        raise InvalidTestError("can't find a valid timestamp in mixing time column")
        
    #create column of formulas that allow xl to calculate time diff
    #do this instead of calculating here (even though it is easier)
    #so that excel has access to the formulas, to make future editing easier
    
    #initialize to length of other data arrays, to simplify paste operation later
    mixing_time_elapsed = ["" for x in range(len(mixing_time_data))]
    
    #figure out which column in excel will contain elapsed column
    for column in range(len(raw_data)):
        if raw_data[column][0] == mixing_col_header:
            xlcol = column + 1 # +1 bc excel is 1-index based
            break
    else:
        raise InvalidTestError("Failed to find mixing column header", raw_data)
        
    xlrowstart = index + xllib.PY_TO_XL_ROW
    xlrowend = len(mixing_time_elapsed) + 2 #+1 for header, +1 for 1-based index
    
    #86400 is conversion of xl time units to seconds
    mixing_time_elapsed[index:] = ["=({}-{})*86400".format(
                                                          xllib.cellstr(current_row, xlcol),
                                                          xllib.cellstr(xlrowstart, xlcol, 1, 1)) 
                                                          for current_row in range(index + xllib.PY_TO_XL_ROW, 
                                                                                   len(mixing_time_elapsed) + xllib.PY_TO_XL_ROW)]

    

    #find initial conductivity, final conductivity ave over 80 sec,
    #t95                       
    initial_conductivity = mixing_PV_data[index]
    
    #find index of timestamp for start of last 80 sec

    end_time = mixing_time_data[-1]
    for i in xllib.rev_range(len(mixing_time_data)):
        t = mixing_time_data[i]
        
        if end_time - t > (80 / xllib.XL_TIME_TO_SEC):
            i += 1 #went too far
            break
    
    final_conductivity_ave = sum(mixing_PV_data[i:])/len(mixing_PV_data[i:])
    
    #find index where PV reaches 95% of final value 
    cond_95pc_final = final_conductivity_ave - (final_conductivity_ave - initial_conductivity) * 0.95 
    for i in xllib.rev_range(len(mixing_PV_data)):
        pv = mixing_PV_data[i]
        if pv < cond_95pc_final:
            i += 1 #went too far
            break
            
    #placeholder; use to calculate formula later
    t_95pc = i
    
    #make a column with conductivity data
    cond_PV = ["" for i in range(len(mixing_PV_data))]
    
    #not a fan of lambdas, so here's this
    def calc_con_PV(raw, rmax=final_conductivity_ave, rmin=initial_conductivity):
        return (raw*1000*(rmax-rmin)/3520) + (rmin - (rmax-rmin)/4)
    
    cond_PV[index:] = [calc_con_PV(raw_measure) for raw_measure in mixing_PV_data[index:]]
    
    
    
    #put everything in excel
    cond_time_col = column + 4
    cond_PV_col = column + 5
    
    #-1 to go from py to xl index base
    raw_data.insert(cond_time_col - 1, ['ElapsedTime'] + mixing_time_elapsed) 
    raw_data.insert(cond_PV_col - 1, ['Conductivity'] + cond_PV)
    xl_raw = tuple(zip_longest(*raw_data, fillvalue=""))
    
    #xlcolend is final col with PV values, after adding
    #column for conductivity
    xlcolend = len(xl_raw[0])
    xlrowend = len(xl_raw)
    
    
    #now that we finally have xlcolend, can figure out what to put down for t_95pc
    #old t_95pc was row where t_95 occurred.
    t_95pc_formula = "={}".format(xllib.cellstr(t_95pc + 1, xlcolend+4))
    
    cells.Range(cells(1,1), cells(xlrowend, xlcolend)).Value = xl_raw 
    cells.Range(cells(1, xlcolend+2), cells(2, xlcolend+4)).Value = (
                                                                     ("Initial Conductivity", "Final Conductivity", "T95"),
                                                                     (initial_conductivity, final_conductivity_ave, t_95pc_formula)
                                                                     )
                                                                     
    results['t95'] = cells(2, xlcolend+4).Value    
    
    for i in xllib.xlrange(xlcolend+3):
        ws.Columns(i).EntireColumn.AutoFit()
        
    chart = xllib.CreateChart(ws, Left=50*column)
    
    #name chart after filename and power input 
    chart_name = filename + "  %s LPM" % (data['AgMainGasActualRequest(LPM)']['PV'][-1])
    chart_source = cells.Range(cells(xlrowstart, cond_time_col), cells(xlrowend, cond_PV_col))
    
    xllib.FormatChart(chart, 
                       SourceData=chart_source, 
                       ChartTitle=chart_name, 
                       xAxisTitle="Time (seconds)", 
                       yAxisTitle=mixing_col_header,
                       Trendline=False)
    
#     print(len(data['pHARaw']['Time']))
    compile_data(chart.Parent)
    return results




def guess_mixing_col_header(data, *, g1='pHARaw', g2='pHBRaw'):
    
    """guess which column is used to collect conductivity
    values for mixing time test. Last time, we used pHBRaw,
    but I set logger to record both pHA and pHB, and I knew
    what was set. This program doesn't, so it must guess.

    Current logic- correct column is either phbraw or pharaw.
    Correct column is also the one with the biggest difference
    between the first and last raw value recorded for that column.
    """

    g1dat = data[g1]['PV']
    g2dat = data[g2]['PV']
    
    guessed_column_header = g1 if (abs(g1dat[0] - g1dat[-1]) > abs(g2dat[0] - g2dat[-1])) else g2  

    return guessed_column_header


def compile_data(old_chart_obj):
    
    charts_per_row = 4
    chart_objs = sum_ws.ChartObjects()
    chart_count = chart_objs.Count

    chart = old_chart_obj.Chart
    chart.ChartArea.Copy()
    sum_ws.Paste()
        
    chart_obj = chart_objs(chart_count)
        
    chart_width = old_chart_obj.Width
    chart_height = old_chart_obj.Height
        
    chart_left = (chart_count % charts_per_row) * chart_width
    chart_top = (chart_count // charts_per_row) * chart_height
        
    chart_obj.Height = chart_height
    chart_obj.Width= chart_width
    chart_obj.Left = chart_left
    chart_obj.Top = chart_top
        
        
 
    
def main():
    batch_files = ["C:/Users/PBS Biotech/Downloads/conductivity/mt 1.2.csv", "C:/Users/PBS Biotech/Downloads/conductivity/mt 1.3.csv"]
#     batch_files = xllib.AskBatchFiles("Mixing Time").execute()
    analyzed_files = []
    broken_files = []
    savedir = "C:\\Users\\Public\\Documents\\PBSSS\\conductivity analysis\\500L New Wheel\\"
    
    xl, wb, ws, cells = xllib.xlobjs()
    xl.Visible=False
    xl.DisplayAlerts = False
    f_ext = '.xlsx'
    
    global sum_wb
    global sum_ws
    
    sum_wb = xl.Workbooks.Add()
    if not sum_wb.Worksheets.Count:
        sum_wb.Worksheets.Add()
    sum_ws = sum_wb.Worksheets(1)
    
    for file_number, file in enumerate(batch_files):
        
        filename = xllib.getFilename(file)
        print("Progress: %d/%d" % (file_number + 1, len(batch_files)))
        print("Attempting to analyze %s..." % filename)
        filename = ''.join([savedir, filename, f_ext]) 
        
        try:
            #main analysis loop here
            analyzed_files.append((filename, run_mixing_analysis(wb, file)))
            
        except Exception as e:
            #make a list of files where errors occurred during attempted analysis
            print("Error analyzing file: ", file)
            print(e)
            broken_files.append(file)
#             
#         except Exception as e:
#             print("Fatal error, aborting analysis:\n", e)
#             raise
#             
        else:
            #ensure FileFormat and extension match if this is changed!
            wb.SaveAs(Filename=filename, FileFormat=xllib.xlOpenXMLWorkbook)
            wb.CloseDialog()
            wb=xl.Workbooks.Add()
        
    if len(analyzed_files):
        print("success! %d/%d files analyzed" % (len(analyzed_files), len(batch_files)))
    
    if len(broken_files) != 0:
        print("Errors were encountered analyzing the following files:")
        for file in broken_files:
            print(file)
            
    wb.CloseDialog()
    
    filename = ''.join([savedir, "Compiled Data", f_ext])
    sum_wb.SaveAs(Filename = filename, FileFormat=xllib.xlOpenXMLWorkbook)
    print(filename)
    
    xl.DisplayAlerts = True
    xl.Quit()
        
if __name__ == "__main__":
    pass
#     main()
   
