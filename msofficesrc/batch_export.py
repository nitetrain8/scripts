"""
Created on Jan 20, 2014

@Company: PBS Biotech
@Author: Nathan Starkweather
"""

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename
from officelib.xllib import Excel, cellStr, cellRangeStr, xlDown, createChart, formatChart, xlLocationAsNewSheet


class SimpleEntry(tk.Entry):
    
    def __init__(self, *args, **kwargs):
        
        self.var = kwargs.get('textvariable', tk.StringVar())
        kwargs["textvariable"] = self.var
        
        super().__init__(*args, **kwargs)
        
    @property
    def text(self):
        return self.var.get()
        
    @text.setter
    def text(self, text):
        self.var.set(text)


class ExportProofHandler():
        
    def __init__(self):
            
        self.root = tk.Tk()
        self.reactor_label = ttk.Label(self.root, text="Reactor Name:")
        self.reactor_name = SimpleEntry(self.root, width=20)
        
        self.ok_btn = ttk.Button(self.root, text="Run", command=self.run)
        self.cancel_btn = ttk.Button(self.root, text="Cancel", command=self.end)
        
        self.date_label = ttk.Label(self.root, text="Batch by Date")
        self.date_entry = SimpleEntry(self.root, width=50)
        self.date_open = ttk.Button(self.root, text="Open", command=self.get_date_name)
        self.date_name = None
        
        self.batch_label = ttk.Label(self.root, text="Batch by Batch")
        self.batch_entry = SimpleEntry(self.root, width=50)
        self.batch_open = ttk.Button(self.root, text="Open", command=self.get_batch_name)
        self.batch_name = None
        
        self.date_label.grid(row=2, sticky=tk.W)
        self.date_entry.grid(row=3, columnspan=3)
        self.date_open.grid(row=3, column=3)
        
        self.batch_label.grid(row=4, sticky=tk.W)
        self.batch_entry.grid(row=5, columnspan=3)
        self.batch_open.grid(row=5, column=3)
        
        self.ok_btn.grid(row=6, column=1, sticky=tk.W)
        self.cancel_btn.grid(row=6, column=0, sticky=tk.E)
        
        self.reactor_label.grid(row=0, sticky=tk.W)
        self.reactor_name.grid(row=1, sticky=tk.W)
        
        self.files = None
        
        self.root.bind_class(self.ok_btn.winfo_class(), "<Return>", self.invoke)
        
    def invoke(self, event):
        event.widget.invoke()
        
    def execute(self):
        self.root.mainloop()
        return self.files
        
    def get_batch_name(self):
        
        name = askopenfilename()
        if name:
            self.batch_entry.text = name

    def get_date_name(self):
        
        name = askopenfilename()
        if name:
            self.date_entry.text = name
            
    def end(self):
        self.root.destroy()
            
    def run(self):
        
        reactor_name = self.reactor_name.text        
        date_name = self.date_entry.text
        batch_name = self.batch_entry.text
        
        if not reactor_name:
            print("Enter reactor name")
            return
        
        if not date_name and not batch_name:
            print("Enter at least one file to analyze")
            return
        
        self.files = {'Date' : date_name,
                      'Batch' : batch_name,
                      'Reactor' : reactor_name or ''}
        
        self.end()        
    
    
def FindTempPV(rangeObj):        
    return rangeObj.Find(What='TempPV(C)', After=rangeObj(1,1))


def MakeChart(xl, reactor_name, filename, export_by):
    
    wb = xl.Workbooks.Open(filename)
    ws = wb.Worksheets(1)
    cells = ws.Cells
    
    target_cell = FindTempPV(cells)
    time_col = target_cell.Column
    pv_col = time_col + 1 
    end_row = target_cell.End(xlDown).Row
    
    x_data = cellRangeStr(
                          (2, time_col, 1, 1),
                          (end_row, time_col, 1, 1)
                          )
    
    y_data = cellRangeStr(
                          (2, pv_col, 1, 1),
                          (end_row, pv_col, 1, 1)
                            )
                            
    chart = createChart(ws)
    SeriesCollection = chart.SeriesCollection()
    
    for i in range(SeriesCollection.Count, 0, -1):
        SeriesCollection(i).Delete()
        
    Series = SeriesCollection.NewSeries()  
    cell_range = cells.Range
    Series.XValues = cell_range(x_data)
    Series.Values = cell_range(y_data)

    ChartTitle = ' '.join((
                           reactor_name,
                           'Export by',
                           export_by
                            ))
                            
    XAxisTitle = 'Time(date)'
    YAxisTitle = 'TempPV'

    formatChart(chart, ChartTitle=ChartTitle,
                        xAxisTitle=XAxisTitle,
                        yAxisTitle=YAxisTitle)
    
    chart.Location(xlLocationAsNewSheet)
    
    
def main():
    
    e = ExportProofHandler()
    data = e.execute()
    xl = Excel(visible=False)
    reactor_name = data['Reactor']

    errors = []    
    try:
        MakeChart(xl, reactor_name, data['Date'], 'Date')
    except BaseException as e:
        errors.append(e)
        
    try:
        MakeChart(xl, reactor_name, data['Batch'], 'Batch')
    except BaseException as e:
        errors.append(e)
        
    print(errors)
    
    xl.Visible = True
    
  
if __name__ == '__main__':
    main()

    
