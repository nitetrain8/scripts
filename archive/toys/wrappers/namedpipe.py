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

from .winstructs import SECURITY_ATTRIBUTES
from .defines import *


_cnp_proto = ctypes.WINFUNCTYPE(wintypes.HANDLE, wintypes.LPCSTR,
                                wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                                wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                                ctypes.POINTER(SECURITY_ATTRIBUTES))

DEFAULT_OPENMODE = PIPE_ACCESS_DUPLEX | FILE_FLAG_FIRST_PIPE_INSTANCE
DEFAULT_PIPEMODE = PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS

_cnp_param_flags = (
    (1, "lpName", None),
    (1, "dwOpenMode", DEFAULT_OPENMODE),
    (1, "dwPipeMode", DEFAULT_PIPEMODE),
    (1, "nMaxInstances", 1),
    (1, "nOutBufferSize", 1 << 16),  # 65536
    (1, "nInBufferSize", 1 << 16),
    (1, "nDefaultTimeOut", 0),
    (1, "lpSecurityAttributes", None)
)

def _cnp_errcheck(result, func, args):
    if result == INVALID_HANDLE_VALUE:
        raise ctypes.WinError()
        # return result

_cnp = _cnp_proto(("CreateNamedPipeA", ctypes.windll.kernel32), _cnp_param_flags)
_cnp.restype = wintypes.HANDLE


def CreateNamedPipe(lpName, dwOpenMode=DEFAULT_OPENMODE,
                    dwPipeMode=DEFAULT_PIPEMODE,
                    nMaxInsances=1, nOutBufferSize=65536, nInBufferSize=65536, nDefaultTimeout=0,
                    lpSecurityAttributes=None):

    h = _cnp(lpName, dwOpenMode, dwPipeMode, nMaxInsances, nOutBufferSize, nInBufferSize, nDefaultTimeout,
             lpSecurityAttributes)
    return h
