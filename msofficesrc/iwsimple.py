"""
Created on Oct 28, 2013

@author: PBS Biotech
"""
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilenames
import os.path




class DialogIncompleteError(Exception):
    pass

class ImportDialog():

    """once dlg is done, call get_analysis_type to get type of analysis,
    and get_raw_files to get list of raw files to analyze
    """

    def __init__(self):
        """ a good programmer would make everything here
        a class variable. oh well.
        """

        '''Setup controls for root'''
        self.root = tk.Tk()
        self.mframe = ttk.LabelFrame(self.root)

        # unused for now
#         self.nextbtn = ttk.Button(self.root, command=self.nextbtncmd, width=10, text="Next >>")
#         self.prevbtn = ttk.Button(self.root, command=self.prevbtncmd, width=12, text="<< Previous")

        '''Container variables'''
        self.fname = tk.StringVar(self.mframe)
        self.analysis_type = tk.StringVar(self.mframe)
        self.atypes = ["kla", "pressure decay", "mixing time"]
        self.raw_files = []

        '''Controls for mframe'''
        # menuoption widget fails to show first item in option list
        # once another option is selected, so use dummy entry as first
        # entry.
        # include dummy menu item in list sent to analysis menu
        # without having to add it to list that keeps track
        # of available analyses.
        defaultmenutext = "No test selected"
        menuops = self.atypes[:]
        menuops.insert(0, defaultmenutext)

        self.analysismenu = ttk.OptionMenu(self.mframe, self.analysis_type, *menuops)
        self.analysismenu.config(width=20)

        self.flistbox = tk.Listbox(self.mframe, width=60, selectmode=tk.EXTENDED)
        self.fnamebox = ttk.Entry(self.mframe, textvariable=self.fname)
        self.browsebtn = ttk.Button(self.mframe, command=self.browsebtncmd, width=10, text="Browse")
        self.runbtn = ttk.Button(self.mframe, command=self.end_prompt, width=10, text="Run")
        self.analysislabel = ttk.Label(self.mframe, text="Select analysis type:")
        self.errorlabel = ttk.Label(self.mframe, text="")

        '''Grid controls for first screen to show'''
        self.show_select_file_screen()

        '''msc setup'''
        self.allowedfiletypes = ["{Text CSV} {.csv .txt}", "{Excel 2007+} {.xlsx .xls}", "{All} {.xlsx .xls .csv .txt}"]
        self.workdir = "C:/Users/Public/Documents/PBSSS"
        self.flistbox.bind("<Key>", self.flistbox_keypressed)
        self._complete = False

    def browsebtncmd(self):

#         #ifdef DEBUG
#         debug_initialdir = "C:/Users/PBS Biotech/Downloads"
#         self.workdir = debug_initialdir
#         #endif //DEBUG

        tclfilestring = askopenfilenames(filetypes=self.allowedfiletypes,
                                 multiple=True,
                                 initialdir=self.workdir)

        # tcl list format -> python list format
        files = tclfilestring.strip("{}").split("} {")

        # break early if askopenfilenames returns empty string (no files selected)
        if files == ['']:
            return

        for file in files:
            if file not in self.raw_files:
                self.raw_files.append(file)



        self.flist_redraw_items()


    def execute(self):
        self.root.mainloop()
        if self._complete == True:
            return {'Test' : self.get_analysis_type(), 'Files' : self.get_raw_files()}
        else:
            '''If dlg ended early, raise error to indicate. Let caller try/except if they want to 
            handle in some other way'''
            raise DialogIncompleteError("dialog terminated before completion")


    def flist_redraw_items(self):
        """whenever adjusting list of raw files,
        delete everything from flistbox and reinsert
        everything from filelist so they are always
        synced
        """

        self.flistbox.delete(0, tk.END)
        self.flistbox.insert(tk.END, *self.raw_files)


    def flistbox_keypressed(self, event):
        keysym = event.keysym
        if keysym == 'BackSpace' or keysym == 'Delete':
            selection = [int(x) for x in self.flistbox.curselection()]
        else:
            return

        for i in selection:
            file = self.flistbox.get(i)
            self.raw_files.remove(file)

        self.flist_redraw_items()

    def show_select_file_screen(self):
        """Show screen to select raw files for analysis"""

        # listbox's row and column span determine placement of other
        # widgets
        lb_rowspan = 8
        lb_colspan = 7

        self.mframe.config(text="Raw File List:")
        self.mframe.grid(row=0, column=0, columnspan=7, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.fnamebox.grid(row=lb_rowspan, columnspan=lb_colspan, sticky=(tk.E, tk.W))
        self.flistbox.grid(row=0, rowspan=lb_rowspan, columnspan=lb_colspan, sticky=(tk.W, tk.E))
        self.browsebtn.grid(row=lb_rowspan, column=lb_colspan - 1, sticky=tk.E)
        self.analysismenu.grid(row=0, column=lb_colspan, sticky=(tk.E, tk.W))
        self.runbtn.grid(row=lb_rowspan, column=lb_colspan, sticky=tk.W)
        self.analysislabel.grid(row=0, column=lb_colspan, sticky=(tk.E, tk.W, tk.N))
        self.errorlabel.grid(row=1, column=lb_colspan, sticky=(tk.E, tk.W, tk.N, tk.S))

    def ungridall(self, master):
        for slave in master.grid_slaves():
            slave.grid_remove()


    def end_prompt(self):
        """check stuff is valid, then exit tkinter dlg
        """
        if self.check_final() == True:
            self.root.destroy()

    def check_final(self):

        self.set_error_label("")
        if not (self.analysis_type.get() in self.atypes):
            self.set_error_label("no analysis selected")
            self._complete = False
            return False

        if len(self.raw_files) == 0:
            self.set_error_label("empty file list")
            self._complete = False
            return False

        self._complete = True
        return True

    def set_error_label(self, message):
        if message != "":
            message = "Error: %s" % message
            print(message)

        self.errorlabel.config(text=message)

    def get_raw_files(self):
        return self.raw_files

    def get_analysis_type(self):
        return self.analysis_type.get()

# from pbsdbg import view_coords


class AskBatchFiles(ImportDialog):

    """Class to call from other script to get an IW dlg"""

    def __init__(self, test_type):
        """call main __init__ and then do some
        sloppy cleanup to turn the dialog into a form
        suitable to be called from other scripts.
        This is currently horrible. Fixing this majorly on Todo list
        but it works. """

        super().__init__()
        if test_type.lower() not in self.atypes:
            raise NameError("Invalid test requested")

        self.analysislabel.grid_forget()
        self.analysismenu.grid_forget()
        self.analysis_type.set(test_type)

    def execute(self):
        self.root.mainloop()
        if self._complete == True:
            return self.get_raw_files()
        else:
            '''If dlg ended early, raise error. Let caller try/except,
            but don't fail silently'''
            raise DialogIncompleteError("dialog terminated before completion")



# debug stuff
if __name__ == "__main__":


    dbg = AskBatchFiles('KLA')
#     print(dir(dbg.mframe.master))
#     print(dbg.root.master)
#     print(dbg.root.grid_slaves())
    from pbsdbg import view_coords
    import sys


    debug = view_coords(dbg.mframe)

    print(dir(dbg.mframe))
    dbg.execute()
#     dbg.execute()
#     dbg.execute()
