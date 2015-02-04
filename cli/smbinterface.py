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
import io
import subprocess
from collections import OrderedDict


class MySMBConnection(SMBConnection):
    pass


class DirEntry():
    def __init__(self, entry, share, path):
        assert isinstance(entry, (SharedFile, SharedDevice))
        self.entry = entry
        if isinstance(entry, SharedFile):
            self.name = entry.filename
            self.isDirectory = entry.isDirectory
        else:
            self.name = entry.name
            self.isDirectory = True

        self.share = share
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

    def update_box(self, contents, share=None, path=None):
        self._emap.clear()

        for c in contents:
            if not isinstance(c, DirEntry):
                c = DirEntry(c, share, path)
            self._emap[str(c)] = c

        self.box.delete(0, tk.END)
        self.box.insert(tk.END, *self._emap)

    def setup(self):
        root = tk.Tk()
        frame = ttk.LabelFrame(root, text="Stupid SMB Thing")
        box = tk.Listbox(frame, width=60)
        close = ttk.Button(root, text="Close", command=lambda: root.destroy)
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

        self.con = MySMBConnection(self.user, self.password, self.myname, self.remote_name)
        if not self.con.connect(self.ipv4):
            raise ValueError("Connection failed to authenticate!")
        shares = self.con.listShares()
        self.update_box(shares)
        root.grid()
        frame.grid(columns=8)
        box.grid(columnspan=8)
        close.grid(column=1)
        upbtn.grid(column=2)
        uploadbtn.grid(column=3)
        new_direct.grid(column=4)

        self.is_setup = True
        box.bind("<Double-Button-1>", self.listbox_dblclick)

    def main(self):
        if not self.is_setup:
            self.setup()
        self.root.mainloop()

    def up_button_click(self):
        try:
            self.path.pop()
        except IndexError:
            pass
        self.show_path(self.path)

    def _generate_path(self, path):
        try:
            share, *pth = path
        except ValueError:
            share = None
            pth = "\\"
        else:
            if pth:
                pth = "\\".join(str(s) for s in pth)
            else:
                pth = "\\"
        return share, pth

    def show_path(self, path):
        share, pth = self._generate_path(path)
        if share is None:
            self.update_box(self.con.listShares(), share, pth)
        else:
            files = self.con.listPath(share, pth)
            self.update_box(files, share, pth)

    def _download_byname(self, share, pth, name, show=True):
        buf = io.BytesIO()
        dlpth = os.path.join(self.dl_path, name)
        smb_name = "\\".join((pth, name))
        attrs, nbytes = self.con.retrieveFile(share, smb_name, buf)
        with open(dlpth, 'wb') as f:
            f.write(buf.getvalue())
        dlpth = dlpth.replace("/", "\\")
        if show:
            cmdpth = "\\".join(dlpth.split("\\")[:-1])
            if " " in cmdpth:
                cmdpth = '"%s"' % cmdpth
            subprocess.Popen("explorer.exe " + cmdpth)

    def download(self, entry, show=True):
        name = entry.name
        share, pth = entry.share, entry.path
        self._download_byname(share, pth, name, show)

    def listbox_dblclick(self, e):
        txt = self.box.get(self.box.curselection()[0])
        entry = self._emap[txt]

        if entry.isDirectory:
            self.path.append(entry)
            try:
                self.show_path(self.path)
            except:
                self.path.pop()
                raise
        else:
            # entry was a file: download and show in folder
            self.download(entry, True)

    def upload(self, share, path, filename):
        assert share, "Don't know how to handle empty share"
        with open(filename, 'rb') as f:
            self.con.storeFile(share, path, f)

    def upload_btn_click(self, e):
        names = askopenfilenames()
        share, path = self._generate_path(self.path)
        lstnames = names.strip("{}").split("} {")
        for name in lstnames:
            self.upload(share, path, name)

    def new_directory(self, share, path):
        self.con.createDirectory(share, path)

    def new_directory_clicked(self, e):
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

        share, pth = self._generate_path(self.path)
        pth = "\\".join((pth, name))
        self.new_directory(share, pth)




def main():
    # print("main", flush=True)
    usr = 'nstarkweather'
    pwd = 'Nate9914#'
    myname = "PBS-TOSHIBA"
    remote = "integritysvr01".upper()
    ipv4 = '192.168.1.99'
    s = SMBInterface(usr, pwd, myname, remote, ipv4)
    # debug
    # s.path = ['Mfg Released', "IF", "IF00102"]
    # s.relist_path()
    s.main()

if __name__ == '__main__':
    try:
        main()
    except:
        input()
