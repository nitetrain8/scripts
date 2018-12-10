"""

Created by: Nathan Starkweather
Created on: 04/02/2016
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import logging

logger = logging.getLogger(__name__)
_h = logging.StreamHandler()
_f = logging.Formatter("%(created)s %(name)s %(levelname)s (%(lineno)s): %(message)s")
_h.setFormatter(_f)
logger.addHandler(_h)
logger.propagate = False
logger.setLevel(logging.DEBUG)
del _h, _f


import ctypes
from ctypes import wintypes
from .winstructs import LPSECURITY_ATTRIBUTES, LPOVERLAPPED
from .defines import *


# CreateFile()

_cf_proto = ctypes.WINFUNCTYPE(wintypes.HANDLE, wintypes.LPCSTR, wintypes.DWORD, wintypes.DWORD,
                               LPSECURITY_ATTRIBUTES, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE)

_CreateFile = _cf_proto(("CreateFileA", ctypes.windll.kernel32))


def CreateFile(filename, access=GENERIC_READ | GENERIC_WRITE,
               sharemode=0, security_attributes=NULL, creation_disposition=OPEN_EXISTING,
               flags_and_attributes=0, template=NULL):
    h = _CreateFile(filename, access, sharemode, security_attributes,
                    creation_disposition, flags_and_attributes, template)
    if h == INVALID_HANDLE_VALUE:
        raise ctypes.WinError()
    return h


# WriteFile()
_wf_proto = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HANDLE, wintypes.LPCVOID, wintypes.DWORD,
                               wintypes.LPDWORD, LPOVERLAPPED)
_WriteFile = _wf_proto(("WriteFile", ctypes.windll.kernel32))


def WriteFile(handle, msg, overlapped=None):
    sz = len(msg)
    written = wintypes.DWORD(0)
    success = _WriteFile(handle, msg, sz, ctypes.byref(written), overlapped)
    if not success:
        raise ctypes.WinError()
    return written.value


# ReadFile()

_rf_proto = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
                               wintypes.LPDWORD, LPOVERLAPPED)
_ReadFile = _rf_proto(("ReadFile", ctypes.windll.kernel32))


def ReadFile(handle, n, overlapped=None):
    buffer = (ctypes.c_char * n)()
    nread = wintypes.DWORD(0)
    success = _ReadFile(handle, buffer, n, ctypes.byref(nread), overlapped)
    if not success:
        raise ctypes.WinError()
    return ctypes.string_at(buffer, nread.value)

