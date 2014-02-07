'''
Created on Dec 2, 2013

@author: PBS Biotech
'''


import tkinter as tk
import tkinter.ttk as ttk
import officelib.olutils
import nsdbg

sticky_all = (tk.E, tk.W, tk.S, tk.N)

class DialogIncompleteError(Exception):
    pass
    


            
        

# @nsdbg.traceClassCalls
@nsdbg.TkViewCoords('__frame1')
class Importer(metaclass=nsdbg.dbgPrintEmptyMeta):
    
    '''Importer class for providing a simple user form to 
    import and analyze batch files, and output the analyzed
    files as excel spreadsheets.'''
    
    
    analysis_types = ['kla', 'mixing time', 'pressure decay']
    allowed_file_types = ["{Text CSV} {.csv .txt}", "{Excel 2007+} {.xlsx .xls}", "{All} {.xlsx .xls .csv .txt}"]
    
    workdir = officelib.olutils.getWorkDir()
    
    
    try:
        dl_dir = officelib.olutils.getDownloadDir()
    except FileNotFoundError:
        dl_dir = workdir    
        
    
    f_colspan = 10
    f_rowspan = 4
    lb_colspan = f_colspan - 2
    lb_rowspan =f_rowspan
    lb_width = 60
    cbtn_width = 10
    te_width = lb_width-cbtn_width
    
    
    def __init__(self, *, type=None):
        
        f_colspan = self.f_colspan
        f_rowspan = self.f_rowspan
        lb_colspan = self.lb_colspan
        lb_rowspan = self.lb_rowspan
        lb_width = self.lb_width
        te_width = self.te_width
        cbtn_width = self.cbtn_width
    
        
        '''Todo: if type is not none, load analysis-specific 
        settings. Actually this should be easy, just use a redirect function
        and separate classes.'''
        assert type is None, "Type choice not yet implemented" 
        
        '''Masters.'''
        self.__root = tk.Tk()
        self.__frame1 = ttk.LabelFrame(self.__root)
        
        '''To avoid having to type self.... everywhere'''
        _r = self.__root
        _f = self.__frame1
        
        '''Nav widgets'''
        self.__prev_btn = ttk.Button(_r, text="<< Previous", command=self.__StepPrev)
        self.__next_btn = ttk.Button(_r, text="Next >>", command=self.__StepNext)
        self.__help_btn = ttk.Button(_r, text="Help", command=self.__ShowHelpPage)
        self.__run_btn = ttk.Button(_r, text="Run", command=self.__Finalize)
        
        '''frame1 widgets and textvariables'''
        
        self.__browse_query = tk.StringVar(_f)
        self.__browse_entry = ttk.Entry(_f, textvariable=self.__browse_query)
        
        #menuoption widget fails to show first item in option list
        #once another option is selected, so use dummy entry as first 
        #entry. 
        #include dummy menu item in list sent to analysis menu 
        #without having to add it to list that keeps track
        #of available analyses.
        self.analysis_types = ["kla", "mixing time", "pressure decay"]
        _m_default = "No test selected"
        self.test_type = tk.StringVar(_f)
        self.__testmenu = ttk.OptionMenu(_f, self.test_type, *([_m_default] + self.analysis_types))
        self.__testmenu.config(width=20)
        self.__browse_btn = ttk.Button(_f, command=self.__AskFileNames, width=cbtn_width, text="Browse")
        self.__test_label = ttk.Label(_f, text="Select test type:")
        self.__errorlabel = ttk.Label(_f, text="")
        self.__file_list = tk.Listbox(_f, selectmode=tk.EXTENDED)
        
        '''misc setup'''
        self.__step = 0
        self.dialog_complete = False
        self.files = []
        
        '''make widget list'''
        f_colspan = self.f_colspan
        f_rowspan = self.f_rowspan
        self.__widgets_nav = [
                              (self.__prev_btn, {'row':f_rowspan-1, 'column':1}),
                              (self.__next_btn, {'row':f_rowspan-1, 'column':2}), 
                              (self.__help_btn, {'row':f_rowspan-1, 'column':0}),
                              (self.__run_btn, {'row':f_rowspan-1, 'column':3}),
                                ]

        lb_colspan = self.lb_colspan
        lb_rowspan = self.lb_rowspan
        self.__widgets_step1 = [
                                (self.__frame1, {'row':0, 'column':0, 'columnspan':f_colspan, 'sticky':(tk.N, tk.S, tk.E, tk.W)}),
                                (self.__testmenu, {'row':0, 'column':lb_colspan, 'sticky':(tk.E, tk.W)}),
                                (self.__browse_btn,{'row':lb_rowspan, 'column':lb_colspan-1, 'sticky':tk.E} ),
                                (self.__test_label, {'row':0, 'column':lb_colspan, 'sticky':(tk.E,tk.W, tk.N)}),
                                (self.__errorlabel, {'row':1, 'column':lb_colspan, 'sticky':(tk.E, tk.W, tk.N, tk.S)}),
                                (self.__file_list, {'row':0, 'rowspan':lb_rowspan, 'columnspan':lb_colspan, 'sticky':(tk.W,tk.E)}),
                                (self.__browse_entry, {'row':lb_rowspan, 'columnspan':lb_colspan, 'sticky':(tk.E, tk.W)})
                                ]
                                
        #call final setup routines
        self.__ShowNav()
        self.__ShowStep1()
        #         rows, columns = self.__frame1.grid_size()
#         for column in range(columns):
#             self.__frame1.grid_columnconfigure(column, uniform='a', weight=1)
#         
#         for w, d in self.__widgets_step1:
#             rs = int(w.grid_info()['rowspan'])
#             print(w, rs)
#             if rs == 4:
#                 print('hi')
#                 for k,v in self.__dict__.items():
#                     if v is w:
#                         print(k)
        
    def __ShowStep1(self):
        self.__frame1.config(text="Raw File List:")
        for w, ops in self.__widgets_step1:
            w.grid(**ops)
                 
    def __ShowNav(self):
#         self.__prev_btn.grid(sticky=sticky_all)
#         self.__next_btn.grid(sticky=sticky_all)
#         self.__help_btn.grid(sticky=sticky_all)
#         self.__run_btn.grid(sticky=sticky_all)
        for w, ops in self.__widgets_nav:
            w.pack()
    
        
    def __StepPrev(self):
        pass
        
    def __StepNext(self):
        pass
        
    def __ShowHelpPage(self):
        pass
    
    def __Finalize(self):
        pass
        
    def __AskFileNames(self):
        pass
        
    def Help(self):
        return self.__ShowHelpPage()
        
    @property
    def Step(self):
        return self.__step
        
    @property
    def TestType(self):
        return self.test_type.get()
        
    def Execute(self):
        self.__root.mainloop()
        if not self.dialog_complete:
            raise DialogIncompleteError
        return (self.test_type, self.files)
        
    
        
        
from types import MethodType
if __name__ == '__main__':     
    def main():
        i = Importer()
        i.Execute()
    

    try:
        main()
    except:
        raise
        
        
        
        
        