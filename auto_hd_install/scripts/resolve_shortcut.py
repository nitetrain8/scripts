
"""
Resolve a windows ".lnk" shortcut.
Adapted from: http://timgolden.me.uk/python/win32_how_do_i/read-a-shortcut.html
""" 
import pythoncom
from win32com.shell import shell

def resolve(filename):
  link = pythoncom.CoCreateInstance (
    shell.CLSID_ShellLink,    
    None,
    pythoncom.CLSCTX_INPROC_SERVER,    
    shell.IID_IShellLink
  )
  link.QueryInterface (pythoncom.IID_IPersistFile).Load (filename)
  #
  # GetPath returns the name and a WIN32_FIND_DATA structure
  # which we're ignoring. The parameter indicates whether
  # shortname, UNC or the "raw path" are to be
  # returned. Bizarrely, the docs indicate that the 
  # flags can be combined.
  #
  name, _ = link.GetPath (shell.SLGP_UNCPRIORITY)
  return name