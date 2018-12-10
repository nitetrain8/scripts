import os, sys
os.chdir(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(".\\Scripts")

import regions, cursor, time

my_hwnd = cursor.get_active_window()

def scan(fp=None):
    dragging = False
    isclick = False
    ox,oy = 0,0     
    while True:
        x,y = cursor.get_xy()

        if cursor.is_keydown():
            if not isclick:
                isclick=True
                dragging=True
                ox = x
                oy = y
        else:
            if cursor.is_keydown(0x53):  # s key
                if fp:
                    hwnd = cursor.get_foreground_window()
                    cursor.set_foreground_window(my_hwnd)
                    msg = input("\nvar name: ")
                    cursor.set_foreground_window(hwnd)
                    fp.write("%s = Region(%d, %d, %d, %d)\n"%(msg, x,y, abs(x-ox), abs(y-oy)))
            isclick=False
            dragging=False

        if dragging:
            msg = "x=%d y=%d w=%d h=%d"%(x,y, abs(x-ox), abs(y-oy))
        else:
            msg = "x=%d y=%d"%(x,y)

        print("\r%s"%msg, " "*20,end="")
        time.sleep(0.01)

# with open("test.py", 'w') as f:
#     scan(f)
# import uiactions
# uiactions.login_to_webui()