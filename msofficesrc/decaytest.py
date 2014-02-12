"""
Created on Oct 23, 2013

@author: PBS Biotech
"""

from officelib import *
from tkinter.filedialog import askopenfilenames
import os

work_folder = "C:\\Users\\Public\\Documents\\"
save_folder = "C:\\Users\\Public\\Documents\\PBSSS\\Pressure Testing\\"
# 
def PromptFile():
    
    
    filetypes = sorted(["TextCSV {.txt .csv}", "Excel2007 {.xlsx}", "All {.csv .txt .xlsx .xls}"])
    
    files = askopenfilenames(filetypes=filetypes, multiple=True, title="Select Raw Batch Files", initialdir=work_folder).strip("{}").split("} {")
#     file = "C:\\Users\\PBS Biotech\\Downloads\\2013102312043385.csv"
    return files

def AnalyzePressureDecay(file):
    excel, wb, ws, cells = xlObjs(file)
    
    pcell= cells.Find(What="Pumps&ValvesPressurePV(psi)", After=cells(1,1), SearchOrder = xlByRows)
    pcol = pcell.Column
    endrow = cells(1,pcol).End(xlDown).Row
    
#     ws.Columns(pcol).NumberFormat = "0.00"
    
    agmodecol = cells.Find(What="AgModeUser", After=cells(1,1), SearchOrder=xlByRows).Column + 1
    agstartrow = cells.Find(What=2, After=cells(1,agmodecol), SearchOrder=xlByColumns).Row
    agstarttime = cells(agstartrow, agmodecol - 1).Value
    dates = ws.Range(cells(2,pcol), cells(endrow, pcol)).Value

    for i in range(len(dates)):
        if dates[i][0] > agstarttime:
            break    
    else:
        raise ValueError
    
    elapsed = pcol+1
    startrow = i + 2    
    ws.Columns(elapsed).Insert(Shift=xlToRight)
    ws.Columns(elapsed).NumberFormat = "0.0"
    cells(1, elapsed).Value = "Elapsed Time"
    cells(startrow, elapsed).Value = "=(%s - %s)*1440" % (cellstr(startrow, pcol), cellstr(startrow, pcol, 1, 1))
    cells(startrow, elapsed).AutoFill(Destination=ws.Range(cells(startrow, elapsed), cells(endrow, elapsed)))
    
    chartx = ws.ChartObjects().Count * 240 + 20
    chart = ws.Shapes.AddChart(xlXYScatterLines, chartx, 20, 400, 250).Chart
    
    chart.SetSourceData(ws.Range(cells(startrow,elapsed), cells(endrow, elapsed + 1)))
    
    axes = chart.Axes(AxisGroup=xlPrimary)
    xaxis = axes(1)
    yaxis = axes(2)
    
    xaxis.HasTitle = True
    yaxis.HasTitle = True
    
    xaxis.AxisTitle.Text = "Time (min)"
    yaxis.AxisTitle.Text = "Pressure (psi)"
    
    trendline = chart.SeriesCollection(1).Trendlines().Add()

    trendline.DisplayEquation = True
    trendline.DisplayRSquared = True
    
    chart.HasTitle = True
    Chart.Title.Text = "Pressure Decay"
    
    wbName = wb.Name
    wb.SaveAs(Filename=save_folder + wbName, FileFormat=xlOpenXMLWorkbook, CreateBackup=False)
    wb.Close(False)
    wb = None
    excel.Close()
    excel = None

    
    
if __name__ == "__main__":
    files = PromptFile()
    print(files)
#     if file is not None:
#         AnalyzePressureDecay(file)










