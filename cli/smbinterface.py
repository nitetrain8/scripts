"""

Created by: Nathan Starkweather
Created on: 02/03/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import tkinter as tk
import tkinter.ttk as ttk
from smb.SMBConnection import SMBConnection
from smb.base import SharedFile, SharedDevice
import io
import subprocess
from collections import OrderedDict


class MySMBConnection(SMBConnection):
    pass


class LB_Ent():
    def __init__(self, entry):
        assert isinstance(entry, (SharedFile, SharedDevice))
        self.entry = entry
        if isinstance(entry, SharedFile):
            self.name = entry.filename
            self.isDirectory = entry.isDirectory
        else:
            self.name = entry.name
            self.isDirectory = True

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

    def update_box(self, contents):
        self._emap.clear()

        for c in contents:
            if not isinstance(c, LB_Ent):
                c = LB_Ent(c)
            self._emap[str(c)] = c

        self.box.delete(0, tk.END)
        self.box.insert(tk.END, *self._emap)

    def setup(self):
        root = tk.Tk()
        frame = ttk.LabelFrame(root, text="Stupid SMB Thing")
        box = tk.Listbox(frame, width=60)
        close = ttk.Button(root, text="Close", command=lambda: root.destroy())
        upbtn = ttk.Button(root, text="Up", command=self.bn_up)

        self.root = root
        self.frame = frame
        self.box = box
        self.upbtn = upbtn
        self.closebtn = close

        self.con = MySMBConnection(self.user, self.password, self.myname, self.remote_name)
        if not self.con.connect(self.ipv4):
            raise ValueError("Connection failed to authenticate!")
        shares = self.con.listShares()
        self.update_box(shares)
        root.grid()
        frame.grid(columns=8)
        box.grid(columnspan=8)
        close.grid()
        upbtn.grid()

        self.is_setup = True
        box.bind("<Double-Button-1>", self.lb_click)

    def main(self):
        if not self.is_setup:
            self.setup()
        self.root.mainloop()

    def bn_up(self):
        try:
            self.path.pop()
        except IndexError:
            pass
        self.relist_path()

    def get_current_path(self):
        pth = "\\".join(str(s) for s in self.path[1:]) or "\\"
        if self.path:
            share = self.path[0]
        else:
            share = ""
        return share, pth

    def relist_path(self):
        share, pth = self.get_current_path()
        print(self.path)
        if share:
            files = self.con.listPath(share, pth)
            self.update_box(files)
        else:
            # path empty, show shares instead
            self.update_box(self.con.listShares())

    def lb_click(self, e):
        txt = self.box.get(self.box.curselection()[0])
        entry = self._emap[txt]

        if entry.isDirectory:
            self.path.append(entry)
            try:
                self.relist_path()
            except:
                self.path.pop()
                raise
        else:
            # download
            name = entry.name
            dlpth = os.path.join(self.dl_path, name)
            buf = io.BytesIO()
            share, pth = self.get_current_path()
            smb_name = "\\".join((pth, name))
            print("Downloading file", smb_name)
            attrs, nbytes = self.con.retrieveFile(share, smb_name, buf)
            print("Got nbytes: " + str(nbytes))
            with open(dlpth, 'wb') as f:
                f.write(buf.getvalue())

            dlpth = dlpth.replace("/", "\\")
            cmdpth = "\\".join(dlpth.split("\\")[:-1])
            print(cmdpth)
            if " " in cmdpth:
                cmdpth = '"%s"' % cmdpth
            subprocess.Popen("explorer.exe " + cmdpth)


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
