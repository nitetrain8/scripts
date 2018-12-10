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


# XXX How to get this from a library instead of hardcode?
INVALID_HANDLE_VALUE = -1

# dwOpenMode[in]
# Access Mode
PIPE_ACCESS_DUPLEX = 3
PIPE_ACCESS_INBOUND = 1
PIPE_ACCESS_OUTBOUND = 2

# File Flags
FILE_FLAG_FIRST_PIPE_INSTANCE = 524288
FILE_FLAG_WRITE_THROUGH = -2147483648
FILE_FLAG_OVERLAPPED = 1073741824

# Security Access Modes
WRITE_DAC = 262144
WRITE_OWNER = 524288
ACCESS_SYSTEM_SECURITY = 16777216

# dwPipeMode[in]
# type modes

PIPE_TYPE_BYTE = 0
PIPE_TYPE_MESSAGE = 4

# Read Modes
PIPE_READMODE_BYTE = 0
PIPE_READMODE_MESSAGE = 2

# Wait Modes
PIPE_WAIT = 0
PIPE_NOWAIT = 1

# Remote Client Modes

PIPE_ACCEPT_REMOTE_CLIENTS = 0
PIPE_REJECT_REMOTE_CLIENTS = 8

NULL = None  # ctypes translation

GENERIC_READ  = 0x80000000
GENERIC_WRITE = 0x40000000

FILE_SHARE_DELETE = 0x00000004
FILE_SHARE_READ   = 0x00000001
FILE_SHARE_WRITE  = 0x00000002

CREATE_NEW        = 1
CREATE_ALWAYS     = 2
OPEN_EXISTING     = 3
OPEN_ALWAYS       = 4
TRUNCATE_EXISTING = 5
