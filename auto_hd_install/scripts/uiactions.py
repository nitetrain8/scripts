import cursor, regions
from time import sleep

def login_to_webui():
    # hhello = cursor.find_window('Hello - Google Chrome')
    # cursor.set_foreground_window(hhello)
    # cursor.set_active_window(hhello)
    # sleep(3)
    # cursor.click()
    # if cursor.get_foreground_window() != hhello:
    #     raise ValueError("Failed to set foreground window")
    
    regions.WEBUI_ACTIONTAB.click(0.1)
    sleep(3)
    regions.WEBUI_LOGIN_NAME1.click(0.1)
    pw = "12345"
    for c in pw:
        regions.WEBUI_NUMPAD_REGIONS[c].click(0.5)
    sleep(3)
    return
    regions.WEBUI_ACTIONTAB.click()
    sleep(2)
    regions.WEBUI_ACTIONS_SHOWDESKTOP.click()