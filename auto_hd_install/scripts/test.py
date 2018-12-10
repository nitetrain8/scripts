import sys
sys.path.append("D:\\auto_hd_install\\scripts")
file = __file__
import os
drive = os.path.splitdrive(os.path.abspath(__file__))[0]
print("DRIVE: %s"%drive)

def copy():
    import install
    install.extract_to_desktop()