
import re, subprocess
from subcmd import cmd

def _get_data(k,v):
    q = "reg query %s /v %s" % (k,v)
    p = subprocess.Popen(q, stdout=subprocess.PIPE)
    if p.wait():  # key not found
        return []
    lines = p.stdout.read().decode().splitlines()
    for l in lines:
        l = re.sub("\s+", " ", l.strip())
        vals = l.split(" ")
        if vals[0].lower() == v.lower():
            return vals[2].split(";")

def _set_data(k,v,t,d):
    data = ";".join(d)
    if data:
        dc = "/d %s"%data
    else:
        dc = ""
    c = "reg add %s /v %s /t %s %s /f"%(k,v,t,dc)
    cmd(c)

_DELETE_VALUE = 0
_EMPTY_VALUE = 1
_IGNORE_VALUE = 2
    
def allow_bat():
    key = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Associations"
    value = "LowRiskFileTypes"
    data = _get_data(key,value)
    if ".bat" not in data:
        if not data:
            rv = _DELETE_VALUE
        else:
            rv = _EMPTY_VALUE
        data.append(".bat")
        _set_data(key, value, "REG_SZ", data)
    else:
        rv = _IGNORE_VALUE
    return rv
    
def _delete_data(k,v):
    c = "reg delete %s /v %s /f"%(k,v)
    cmd(c)
    
def disable_bat(action=_DELETE_VALUE):
    key = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Associations"
    value = "LowRiskFileTypes"
    if action == _IGNORE_VALUE:
        return
    elif action == _EMPTY_VALUE:
        data = _get_data(key,value)
        if ".bat" in data:
            data.remove(".bat")
            _set_data(key, value, "REG_SZ", data)
    elif action == _DELETE_VALUE:
        _delete_data(key,value)