"""

Created by: Nathan Starkweather
Created on: 02/03/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilenames
from smb.SMBConnection import SMBConnection
from smb.base import SharedFile, SharedDevice
import smb.base
# from smb.SMBHandler import SMBHandler
import io
import subprocess
from collections import OrderedDict


class MySMBConnection(SMBConnection):
    pass


class YesNo():
    def __init__(self, message):
        self.root = tk.Toplevel()
        frame = ttk.LabelFrame(self.root, text="Yes/No Prompt")
        label = ttk.Label(frame, text=message)
        yes = ttk.Button(frame, text="Yes", command=self.yes)
        no = ttk.Button(frame, text="No", command=self.no)
        self.result = False

        self.root.grid()
        frame.grid()
        label.grid()
        yes.grid()
        no.grid()

    def no(self):
        self.result = False
        self.root.destroy()

    def yes(self):
        self.result = True
        self.root.destroy()

    def run(self):
        # self.root.mainloop()
        self.root.wait_window(self.root)
        return self.result


class DirEntry():
    def __init__(self, entry, svc_name, path):
        assert isinstance(entry, (SharedFile, SharedDevice))
        self.entry = entry
        if isinstance(entry, SharedFile):
            self.name = entry.filename
            self.isDirectory = entry.isDirectory
            self.isShare = False
        else:
            self.name = entry.name
            self.isDirectory = True
            self.isShare = True

        self.svc_name = svc_name
        self.path = path

    def __str__(self):
        return self.name


import os.path
DEFAULT_PATH = "C:\\.replcache\\SMB"


class SMBInterface():

    def __init__(self, usr, pwd, myname, remote_name, ipv4,
                 dl_path=DEFAULT_PATH):

        self.user = usr
        self.password = pwd
        self.myname = myname
        self.remote_name = remote_name
        self.ipv4 = ipv4
        self.is_setup = False
        self.path = []
        self.dl_path = dl_path
        if not os.path.exists(dl_path):
            os.makedirs(dl_path)
        self._emap = OrderedDict()

        self.setup()

    def close(self):
        print("close")
        self.root.destroy()

    def update_box(self, contents, svc_name=None, path=None):
        self._emap.clear()

        for c in contents:
            if not isinstance(c, DirEntry):
                c = DirEntry(c, svc_name, path)
            self._emap[str(c)] = c

        self.box.delete(0, tk.END)
        self.box.insert(tk.END, *self._emap)

    def init_connection(self):
        self.con = MySMBConnection(self.user, self.password, self.myname, self.remote_name)
        print("Connecting...")
        if not self.con.connect(self.ipv4):
            print("Uh Oh")
            raise ValueError("Failed to init connection")
        print("Connected!")

    def setup(self):
        root = tk.Tk()
        frame = ttk.LabelFrame(root, text="Stupid SMB Thing")
        box = tk.Listbox(frame, width=60)
        close = ttk.Button(root, text="Close", command=self.close)
        upbtn = ttk.Button(root, text="Up", command=self.up_button_click)
        uploadbtn = ttk.Button(root, text="Upload...", command=self.upload_btn_click)
        new_direct = ttk.Button(root, text="New Folder", command=self.new_directory_clicked)

        self.root = root
        self.frame = frame
        self.box = box
        self.upbtn = upbtn
        self.closebtn = close
        self.uploadbtn = uploadbtn
        self.new_directory_btn = new_direct

        breakpoint = ttk.Button(root, text="Breakpoint", command=self.breakpoint)
        breakpoint.grid()

        self.init_connection()
        # if not self.con.connect(self.ipv4, timeout=10):
        #     raise ValueError("Connection failed to authenticate!")
        shares = self.con.listShares()
        self.update_box(shares)
        root.grid()
        frame.grid(columns=8)
        box.grid(columnspan=8)
        close.grid(column=1, row=2)
        upbtn.grid(column=2, row=2)
        uploadbtn.grid(column=3, row=2)
        new_direct.grid(column=4, row=2)

        self.is_setup = True
        box.bind("<Double-Button-1>", self.listbox_dblclick)

    def main(self):
        if not self.is_setup:
            self.setup()
        print("mainloop")
        self.root.mainloop()

    def up_button_click(self):
        try:
            self.path.pop()
        except IndexError:
            pass
        self.show_path(self.path)

    def _generate_path(self, path):
        try:
            svc_name, *pth = path
        except ValueError:
            svc_name = None
            pth = "\\"
        else:
            if pth:
                pth = "\\".join(str(s) for s in pth)
            else:
                pth = "\\"
        return svc_name, pth

    def show_path(self, path):
        svc_name, pth = self._generate_path(path)
        count = 1
        while True:
            try:
                if svc_name is None:
                    self.update_box(self.con.listShares(), svc_name, pth)
                else:
                    self.update_box(self.con.listPath(svc_name, pth), svc_name, pth)
            except (OSError, smb.base.NotConnectedError):
                if count > 3:
                    raise
                count += 1
                self.con.close()
                self.init_connection()
            else:
                break

    def show_explorer(self, path):
        print(path)
        path = path.replace("/", "\\")
        cmdpth = "\\".join(path.split("\\")[:-1])
        if " " in cmdpth:
            cmdpth = '"%s"' % cmdpth
        print(cmdpth)
        subprocess.Popen("explorer.exe " + cmdpth)

    def download(self, svc_name, path, filename, topath=None, show=True):

        if topath is None:
            topath = os.path.join(self.dl_path, filename)

        if os.path.exists(topath):
            overwrite = YesNo("File Exists: Overwrite?").run()
            if not overwrite:
                return

        buf = io.BytesIO()
        smb_name = "\\".join((path, filename))
        try:
            attrs, nbytes = self.con.retrieveFile(svc_name, smb_name, buf)
        except:
            print(svc_name, smb_name)
            print(buf.getvalue())
            raise

        with open(topath, 'wb') as f:
            # while some files might be big,
            # the network operation will be much more of a performance
            # drag than just having an extra copy of the contents floating around.
            # so don't bother writing in line by line
            f.write(buf.getvalue())
        if show:
            self.show_explorer(topath)

    def download_entry(self, entry, show=True):
        name = entry.name
        svc_name, pth = entry.svc_name, entry.path
        self.download(svc_name, pth, name, None, show)

    def current_selection(self):
        return self.box.get(self.box.curselection()[0])

    def listbox_dblclick(self, e):
        txt = self.current_selection()
        entry = self._emap[txt]

        if entry.isDirectory:
            self.path.append(entry)
            try:
                self.show_path(self.path)
            except:
                self.path.pop()
                raise
        else:
            # entry was a file: download_entry and show in folder
            self.download_entry(entry, True)

    def upload(self, svc_name, path, filename):
        assert svc_name, "Don't know how to handle empty share"
        print(svc_name, path)
        with open(filename, 'rb') as f:
            try:
                self.con.storeFile(svc_name, path, f)
            except:
                print(svc_name, path)
                raise

    def upload_btn_click(self):
        svc_name, path = self._generate_path(self.path)
        names = askopenfilenames()
        for name in names:
            self.upload(svc_name, os.path.join(path, os.path.split(name)[1]), name)

    def new_directory(self, svc_name, path):
        try:
            self.con.createDirectory(svc_name, path)
        except:
            print(svc_name, path)
            raise

    def new_directory_clicked(self):
        prompt = tk.Toplevel(self.root)
        frame = ttk.LabelFrame(prompt, text="Enter Name of Directory")
        t = tk.StringVar()
        entry = ttk.Entry(frame, width=60, textvariable=t)
        name = None

        def clicked():
            nonlocal name
            name = t.get()
            prompt.destroy()
        btn = ttk.Button(frame, text="Ok", command=clicked)

        prompt.grid()
        frame.grid()
        entry.grid()
        btn.grid()

        prompt.wait_window(prompt)

        svc_name, pth = self._generate_path(self.path)
        pth = "\\".join((pth, name))
        self.new_directory(svc_name, pth)
        
    def delete(self, svc_name, path, isdirectory):
        if isdirectory:
            self.con.deleteDirectory(svc_name, path)
        else:
            self.con.deleteFiles(svc_name, path)

    def delete_clicked(self, e):
        txt = self.current_selection()
        entry = self._emap[txt]
        svc = entry.svc_name
        path = entry.path
        self.delete(svc, path, entry.isDirectory)

    def breakpoint(self):
        import pdb
        pdb.set_trace()
        while False:
            break


def main():
    # print("main", flush=True)
    usr = 'nstarkweather'
    pwd = 'Nate9914#'
    myname = "PBS-TOSHIBA"
    remote = "integritysvr01".upper()
    ipv4 = '192.168.1.99'
    s = SMBInterface(usr, pwd, myname, remote, ipv4)
    # debug
    s.path = ['Data', "Documents", "Posting Matrix"]
    s.show_path(s.path)
    s.main()

if __name__ == '__main__':
    try:
        main()
    except Exception:
        input()
        raise
