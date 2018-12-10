import ctypes
import subprocess
import time
import os

_here = os.path.dirname(__file__)
_dll = os.path.join(_here, "wlan_scan.dll")
_ws = ctypes.cdll.LoadLibrary(_dll)
_scan = _ws.scan
_scan.argtypes=[ctypes.c_int]
_scan.restype = None

def scan(verbose=False):
    return _scan(verbose)

def get_current_wifi():
    lines = subprocess.getoutput("netsh wlan show interfaces").splitlines()
    name = None
    for line in lines:
        try:
            key, val = line.split(":", 1)
        except ValueError:
            continue
        key = key.strip()
        val = val.strip()
        if key == "Name":
            name = val
            continue
        if key == "SSID" and name == "Wi-Fi":
            return val

def connect_wifi(nw):
    if get_current_wifi() == nw:
        print("Already on %s" % nw)
        return
    try:
        subprocess.check_call("netsh wlan connect name=\"%s\""%nw)
    except subprocess.CalledProcessError:
        raise NameError("No network named %r found" % nw) from None
    print("Switched to %s" % nw)


def ensure_wifi(name, timeout=10, vb=False):
    scan(vb)
    start = time.time()
    while True:
        try:
            connect_wifi(name)
        except NameError:
            if timeout > 0 and time.time() - start > timeout:
                raise
        else:
            break
