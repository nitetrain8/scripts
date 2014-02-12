"""
Created on Oct 25, 2013

@author: PBS Biotech
"""
from officelib import *

def createchart(ws, xval, yval, title, xaxistitle, yaxistitle):
    chartx = ws.ChartObjects().Count * 450 + 20
    chart = ws.Shapes.AddChart(xlXYScatterLines, chartx, 20, 400, 250).Chart
    
    seriescollection = chart.SeriesCollection()
    
    if seriescollection.Count:
        series = seriescollection(1)
        for i in xlrange(seriescollection.Count, 2, -1):
            seriescollection(i).Delete()
        
    else:
        series = seriescollection.NewSeries()
            
    wsname = ws.Name
#     print()
    series.XValues = "\'{}\'!{}".format(ws.Name, xval)
    series.Values = "\'{}\'!{}".format(ws.Name, yval)
    
    chart.HasTitle = True
    chart.ChartTitle.Text = title
    
    axes = chart.Axes(AxisGroup=xlPrimary)
    xaxis = axes(1)
    yaxis = axes(2)
    
    xaxis.HasTitle = True
    yaxis.HasTitle = True
    
    xaxis.AxisTitle.Text = xaxistitle
    yaxis.AxisTitle.Text = yaxistitle
    
doc = "C:\\Users\\PBS Biotech\\Dropbox\\PBS Validation (1)\\500Lgasflowrpmchart data\\500L gas flow rpm.xlsx"
# doc = "C:\\Users\\PBS Biotech\\Documents\\Personal\\500L gas flow rpm.xlsx"
xdata = "{}:{}".format(cellstr(5,2,1,1), cellstr(15, 2, 1, 1))    


excel, wb, ws, cells = xlobjs(doc)
xaxistitle = "Gas Flow (LPM)"
yaxistitle = "RPM" 

for i in xlrange(3, 9):
    ydata = "{}:{}".format(cellstr(5, i, 1,1), cellstr(15, i, 1, 1))
    title = "{}L Gas Flow vs. RPM".format(cells(4, i).Value)
    xaxistitle = "Gas Flow (LPM)"
    yaxistitle = "RPM"
#     print("args: ", ws, xdata, ydata, title, xaxistitle, yaxistitle)
    createchart(ws, xdata, ydata, title, xaxistitle, yaxistitle)
