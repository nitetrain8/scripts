import ctypes, os, platform
_p = os.path.dirname(__file__)
_suffix = platform.architecture()[0][:2]
_dllpth = os.path.join(_p, "send_input%s.dll"%_suffix)
_send_input = ctypes.CDLL(_dllpth).send_input
_send_input.argtypes = [ctypes.c_char_p]
_send_input.restype = ctypes.c_int

def send_input(s):
    if not isinstance(s, bytes):
        s = s.encode('ascii')
    _send_input(s)
