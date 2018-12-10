""" This file started out as cursor functions, 
but evolved into more of a ctypes-based winapi
mini-library.
""" 

import ctypes
import time
from ctypes import wintypes

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long)
    ]

class RECT(ctypes.Structure):
        _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

DWORD = wintypes.DWORD
HWND = wintypes.HWND
wintypes.ULONG_PTR = wintypes.WPARAM

_user32 = ctypes.windll.user32

_GetCursorPos = _user32.GetCursorPos
_GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
_GetCursorPos.restype = ctypes.c_int

_SetCursorPos = _user32.SetCursorPos
_SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
_SetCursorPos.restype = ctypes.c_int

_mouse_event = _user32.mouse_event
_mouse_event.argtypes = [DWORD, DWORD, DWORD, DWORD, wintypes.ULONG_PTR]
_mouse_event.restype = None

_SetActiveWindow = _user32.SetActiveWindow
_SetActiveWindow.argtypes = [HWND]
_SetActiveWindow.restype = HWND

_SetForegroundWindow = _user32.SetForegroundWindow
_SetForegroundWindow.argtypes = [HWND]
_SetForegroundWindow.restype = ctypes.c_int

_GetForegroundWindow = _user32.GetForegroundWindow
_GetForegroundWindow.argtypes = []
_GetForegroundWindow.restype = HWND

_GetActiveWindow = _user32.GetActiveWindow
_GetActiveWindow.argtypes = []
_GetActiveWindow.restype = HWND

_FindWindowA = _user32.FindWindowA
_FindWindowA.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
_FindWindowA.restype = HWND

_GetKeyState = _user32.GetKeyState
_GetKeyState.argtypes = [ctypes.c_int]
_GetKeyState.restype = ctypes.c_int


VK_LBUTTON = 0x1
VK_RBUTTON = 0x2

def get_foreground_window():
    return _GetForegroundWindow()
    
def set_foreground_window(hwnd):
    rv = _SetForegroundWindow(hwnd)
    if rv == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return rv
    
def set_active_window(hwnd):
    rv = _SetActiveWindow(hwnd)
    if rv == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return rv
    
def get_active_window():
    return _GetActiveWindow()

def find_window(w):
    if isinstance(w, str):
        w = w.encode('ascii')
    return _FindWindowA(None, w)

def is_keydown(vk=VK_LBUTTON):
    r = _GetKeyState(vk)
    if r & 0x100:
        return True
    return False


def get_xy():
    p = POINT()
    _GetCursorPos(ctypes.byref(p))
    return p.x, p.y

def move(x,y):
    _SetCursorPos(int(x),int(y))

MOUSEEVENTF_LEFTDOWN = 0x2
MOUSEEVENTF_LEFTUP   = 0x4

def click(dx=0, dy=0, data=0, info=0, delay=0.1):
    info = wintypes.ULONG_PTR(info)
    dx=int(dx)
    dy=int(dy)
    data=int(data)
    _mouse_event(MOUSEEVENTF_LEFTDOWN, dx, dy, data, info)
    time.sleep(delay)
    _mouse_event(MOUSEEVENTF_LEFTUP, dx, dy, data, info)
    

def activate(w):
    hwnd = find_window(w)
    if not hwnd:
        raise ValueError("Failed to find window")
    _SetForegroundWindow(hwnd)
    _SetActiveWindow(hwnd)


# from https://stackoverflow.com/questions/13564851/how-to-generate-keyboard-events-in-python
# input structs implementation in python


INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

# msdn.microsoft.com/en-us/library/dd375731
VK_TAB  = 0x09
VK_MENU = 0x12

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

_user32.SendInput.errcheck = _check_count
_user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize