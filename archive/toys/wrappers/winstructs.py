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

class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('nLength', wintypes.DWORD),
        ('lpSecurityDescriptor', wintypes.LPVOID),
        ('bInheritHandle', wintypes.BOOL)
    ]
LPSECURITY_ATTRIBUTES = ctypes.POINTER(SECURITY_ATTRIBUTES)

ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)


class _ovl_unnamed_int_struct(ctypes.Structure):
    _fields_ = [
        ('Offset', wintypes.DWORD),
        ("OffsetHigh", wintypes.DWORD)
    ]


class _ovl_unnamed_union(ctypes.Union):
    _fields = [
        ("struct", _ovl_unnamed_int_struct),
        ("CPointer", ctypes.c_void_p)
    ]


class OVERLAPPED(ctypes.Structure):
    _fields = [
        ("Internal", ULONG_PTR),
        ("InternalHigh", ULONG_PTR),
        ("union", _ovl_unnamed_union),
        ("hEvent", wintypes.HANDLE)
    ]

LPOVERLAPPED = ctypes.POINTER(OVERLAPPED)
