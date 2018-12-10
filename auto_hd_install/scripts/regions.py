import cursor
import os
import time

class Region():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.midx = self.x + self.w / 2
        self.midy = self.y + self.h / 2

    def click(self, speed=1, n=200, wait=0.3):
        mousemove(self.midx, self.midy, speed, n, wait)
        cursor.click()


def mousemove(x,y, speed=1, n=200, wait=0.3):
    cx, cy = cursor.get_xy()
    dx = x - cx
    dy = y - cy
    ndx = dx / n
    ndy = dy / n
    interval = speed / n
    for i in range(int(n)):
        cursor.move(cx+i*ndx, cy+i*ndy)
        time.sleep(interval)
    cursor.move(x,y)
    time.sleep(wait)


LOGIN_SCREEN_FULL     = Region(229,199,335,234)
WELCOME_SCREEN        = Region(75,33,631,562)
KB_SCREEN_EMPTY       = Region(26,213,737,386)
KB_SCREEN_ENTER       = Region(649,444,103,46)
ACCOUNT_BUTTON        = Region(688,3,94,43)
ACCOUNT_MENU_MANAGE   = Region(681,49,86,43)
ACCOUNT_MENU_LOGOUT   = Region(680,96,86,39)
LOGIN_FIELD_NAME      = Region(318,259,149,20)
LOGIN_FIELD_PW        = Region(319,299,145,21)
LOGIN_FIELD_LOGIN     = Region(309,331,76,41)
MANAGE_MENU           = Region(338,43,127,49)
MANAGE_MENU_USERNAME  = Region(180,112,107,18)

KB_0                  = Region(502,348,44,39)
KB_1                  = Region(55,350,40,37)
KB_2                  = Region(102,347,45,40)
KB_3                  = Region(153,348,45,38)
KB_4                  = Region(202,347,48,40)
KB_5                  = Region(255,349,42,39)
KB_6                  = Region(304,347,46,42)
KB_7                  = Region(353,347,44,41)
KB_8                  = Region(404,347,44,44)
KB_9                  = Region(453,348,43,38)
KB_A                  = Region(103,445,46,48)
KB_B                  = Region(327,498,43,40)
KB_C                  = Region(227,495,49,47)
KB_D                  = Region(202,446,51,47)
KB_E                  = Region(177,394,46,49)
KB_F                  = Region(255,445,47,44)
KB_G                  = Region(302,444,53,53)
KB_H                  = Region(356,448,41,42)
KB_I                  = Region(427,396,48,44)
KB_J                  = Region(406,447,42,43)
KB_K                  = Region(455,446,46,44)
KB_L                  = Region(505,447,48,43)
KB_M                  = Region(428,496,44,42)
KB_N                  = Region(376,495,48,51)
KB_O                  = Region(478,395,49,48)
KB_P                  = Region(529,395,43,47)
KB_Q                  = Region(74,394,52,50)
KB_R                  = Region(227,396,46,46)
KB_S                  = Region(154,446,47,44)
KB_T                  = Region(277,396,47,44)
KB_U                  = Region(377,396,48,47)
KB_V                  = Region(276,493,46,48)
KB_W                  = Region(126,395,50,49)
KB_X                  = Region(177,495,47,47)
KB_Y                  = Region(327,396,47,48)
KB_Z                  = Region(127,493,46,47)

WEBUI_NUMPAD1                  = Region(472, 180, 256, 62)
WEBUI_NUMPAD2                  = Region(645, 203, 88, 51)
WEBUI_NUMPAD3                  = Region(743, 203, 90, 54)
WEBUI_NUMPAD4                  = Region(549, 262, 89, 53)
WEBUI_NUMPAD5                  = Region(646, 263, 90, 55)
WEBUI_NUMPAD6                  = Region(743, 261, 90, 51)
WEBUI_NUMPAD7                  = Region(548, 320, 88, 51)
WEBUI_NUMPAD8                  = Region(646, 322, 89, 52)
WEBUI_NUMPAD9                  = Region(744, 322, 90, 53)
WEBUI_NUMPAD_DOT               = Region(551, 381, 91, 53)
WEBUI_NUMPAD0                  = Region(648, 380, 90, 51)

WEBUI_NUMPAD_REGIONS = {
    "1":WEBUI_NUMPAD1,
    "2":WEBUI_NUMPAD2,
    "3":WEBUI_NUMPAD3,
    "4":WEBUI_NUMPAD4,
    "5":WEBUI_NUMPAD5,
    "6":WEBUI_NUMPAD6,
    "7":WEBUI_NUMPAD7,
    "8":WEBUI_NUMPAD8,
    "9":WEBUI_NUMPAD9,
    "0":WEBUI_NUMPAD0,
    ".":WEBUI_NUMPAD_DOT,
}

KEYBOARD_REGIONS = {
    "a": KB_A,
    "b": KB_B,
    "c": KB_C,
    "d": KB_D,
    "e": KB_E,
    "f": KB_F,
    "g": KB_G,
    "h": KB_H,
    "i": KB_I,
    "j": KB_J,
    "k": KB_K,
    "l": KB_L,
    "m": KB_M,
    "n": KB_N,
    "o": KB_O,
    "p": KB_P,
    "q": KB_Q,
    "r": KB_R,
    "s": KB_S,
    "t": KB_T,
    "u": KB_U,
    "v": KB_V,
    "w": KB_W,
    "x": KB_X,
    "y": KB_Y,
    "z": KB_Z,
    "A": KB_A,
    "B": KB_B,
    "C": KB_C,
    "D": KB_D,
    "E": KB_E,
    "F": KB_F,
    "G": KB_G,
    "H": KB_H,
    "I": KB_I,
    "J": KB_J,
    "K": KB_K,
    "L": KB_L,
    "M": KB_M,
    "N": KB_N,
    "O": KB_O,
    "P": KB_P,
    "Q": KB_Q,
    "R": KB_R,
    "S": KB_S,
    "T": KB_T,
    "U": KB_U,
    "V": KB_V,
    "W": KB_W,
    "X": KB_X,
    "Y": KB_Y,
    "Z": KB_Z,
    "0": KB_0,
    "1": KB_1,
    "2": KB_2,
    "3": KB_3,
    "4": KB_4,
    "5": KB_5,
    "6": KB_6,
    "7": KB_7,
    "8": KB_8,
    "9": KB_9,
}

WEBUI_ACTIONTAB                = Region(591, 575, 86, 71)
WEBUI_LOGIN_NAME1              = Region(364, 140, 335, 42)
WEBUI_ACTIONS_SHOWDESKTOP      = Region(766, 417, 164, 49)
SHELLUI_LOGIN_USERNAME         = Region(466, 279, 148, 23)
SHELLUI_LOGIN_PASSWORD         = Region(317, 298, 1, 42)
SHELLUI_LOGIN_LOGIN            = Region(386, 373, 80, 45)
SHELLUI_SYSTEM                 = Region(326, 264, 6, 6)
SHELLUI_SYSTEMMENU_TOOLS       = Region(581, 88, 84, 37)
SHELLUI_SYSTEMTOOLS_REBOOT     = Region(440, 318, 90, 39)
SHELLUI_CONFIG                 = Region(198, 3, 152, 276)
SHELLUI_CONFIGMENU_CALIBRATION = Region(203, 96, 61, 70)
SHELLUI_CALIBRATE_MFC          = Region(784, 88, 72, 34)
SHELLUI_ABOUT                  = Region(587, 6, 125, 48)
AUTH_SBRIO_PASSWORD            = Region(363, 323, 128, 12)
AUTH_SBRIO_RUN                 = Region(281, 215, 17, 18)
AUTH_SBRIO_CLOSE               = Region(519, 151, 162, 3)
NI_REGISTER_USERNAME           = Region(478, 366, 219, 15)
NI_REGISTER_PASSWORD           = Region(480, 401, 223, 21)
NI_REGISTER_NEXT               = Region(566, 502, 66, 16)