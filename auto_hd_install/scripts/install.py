import string
import sys
import os
os.chdir(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(".\\Scripts")
from resolve_shortcut import resolve
from subcmd import cmd, cmd2, cmd3, read_until
import copyprog
import datetime
import time
import sys
import install_pbs
from send_input import send_input
import pickle
import re
import ctypes
import subprocess
from allow_bat import allow_bat, disable_bat
import platform
import cursor, regions
import uiactions

def maybe_handle_touchscreen():
    # Todo
    # Use winapi EnumDisplayDevices to find
    # the device name
    pass

def _check_name(n):
    if len(n) > 16:
        print("Name cannot be longer than 16 characters!")
        return False
    bad = []
    for c in n:
        if c in "\\/:*?\"<>|" or c not in string.printable:
            bad.append(c)
    if bad:
        print("Invalid character(s) in name:", "".join(bad))    
        return False
    return True

def prompt(s, cb):
    while True:
        v = input(s)
        if cb(v):
            return v

def get_computer_name():
    return prompt("Enter Computer Name:", _check_name)

def set_computer_name(name):
    cmd('net config server /srvcomment:"%name%"'.replace("%name%", name))
    name2 = re.sub(r"[\t\r\n ]", "", name).upper()
    cmd('WMIC computersystem where caption="%%COMPUTERNAME%%" rename %s'
        % name2, shell=True)


def _check_date(d):
    fmt = "%m-%d-%y"
    try:
        datetime.datetime.strptime(d, fmt)
    except ValueError:
        print("Date does not match format %r"%(fmt))
        return False
    return True

def _check_time(t):
    fmts = "%H:%M:%S", "%H:%M:%S.%f"
    for f in fmts:
        try:
            time.strptime(t, f)
        except ValueError:
            pass
        else:
            return True
    print("Time must match one of the following formats: %s", " ".join(repr(f) for f in fmts))
    return False

def get_date_time():
    d = prompt("Enter date (mm-dd-yy)", _check_date)
    t = prompt("Enter time (24hr) (HH:MM:SS)", _check_time)
    return d, t

def set_date_time(d, t):
    cmd("date %s"%d, shell=True)
    cmd("time %s"%t, shell=True)

def reboot():
    print("Shutting down in 3 seconds...")
    cmd2("shutdown /r /t 3")
    sys.exit(0)

def select_install_type():
    f = install_pbs.choose_config(INSTALL_RIO_DIR)
    return os.path.join(INSTALL_RIO_DIR, f)


def _cpath(f):
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, f)

def _findf(d, fn):
    f = None
    found = False
    for f in os.listdir(d):
        if fn in f:
            found = True
            break
    if not found or f is None:
        raise FileNotFoundError("Failed to find %r"%fn)
    return f

def install_certs(d):
    # have to find the script name.....
    f = _findf(d, "install_certs")
    c = os.path.join(d, f)
    p = cmd2("\"%s\""%c, shell=True, stdout=subprocess.PIPE)
    read_until(p, b"(y/n):")
    send_input(b"y\r")
    read_until(p, b"Press any key to continue . . .")
    send_input(b"\r")


def schedule_for_startup(py, bat):
    c = 'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /v "PBSInstallReboot" /d "\\"%s\\"" /t REG_SZ /f' %  (bat)
    cmd(c)

DRIVE = os.path.splitdrive(os.path.abspath("."))[0]+"\\"
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
INSTALL_RIO_DIR = os.path.join(DESKTOP, "1 Install RIO")
EXTRACT_DIR = os.path.join(DESKTOP, "Hello Installer.tmp")
STATE_FILE = os.path.join(EXTRACT_DIR, "InstallState.txt")

# Install states
STATE_EXTRACT = 0
STATE_INIT = 1
STATE_INSTALL_PBS = 2

# state_funcs = {
#     STATE_INIT: init,
# }


def check_state():
    try:
        with open(STATE_FILE, 'rb') as f:
            s, data = pickle.load(f)
    except FileNotFoundError:
        return STATE_EXTRACT, None
    return s, data

def set_state(s, data=None):
    global state
    state = s
    with open(STATE_FILE, 'wb') as f:
        pickle.dump((s, data), f)

def check_admin():
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if not is_admin:
        print("Not running as administrator, exit and try again!")
        return False
    return True

def run_recorder(d):
    fp = os.path.join(d, _findf(d, "Recorder.exe"))
    if fp.endswith(".lnk"):
        fp = resolve(fp)
    cmd2(fp)
    # recorder.exe is an application that has to be closed manually, 
    # but doesn't give any reasonable indication of completion.....
    time.sleep(15)
    cmd("tskill.exe \"Recorder\"")
    
def restart_instance(py, bat):
    c = '"%s"' % (bat)
    cwd = os.path.dirname(bat)
    cmd3(c, cwd=cwd)
    sys.exit(0)

def sadmin_allow():
    cmd("sadmin trusted -i %s\\"%os.path.splitdrive(os.path.abspath(__file__))[0])

def sadmin_disallow():
    cmd("sadmin trusted -r %s\\"%os.path.splitdrive(os.path.abspath(__file__))[0])

def sadmin_solidify(fp):
    cmd("sadmin so \"%s\""%fp)

def create_new_batfile(hd_dst, py, bat):
    return
    with open(bat, 'r') as f:
        lines = f.readlines()
    with open(bat, 'w') as f:
        for l in lines:
            if l.lower().startswith("@set python"):
                l = "@Set PYTHON=%s\n" % py
            f.write(l)
    
def extract_to_desktop():
    dn = os.path.dirname  # brevity
    print("Extracting installer files ... ")
    hd_src = dn(dn(os.path.abspath(__file__)))
    hd_dst = os.path.join(EXTRACT_DIR, "auto_hd_install")
    # copy the correct "bitness" python dir
    suffix = platform.machine()[-2:]
    if suffix != "64":
        suffix = ""
    py_src = os.path.join(DRIVE, "Python" + suffix)
    py_dst = os.path.join(EXTRACT_DIR, "Python")
    # # DEBUG!
    # if os.path.exists(py_dst) and os.path.exists(hd_dst):
    #     return None, os.path.join(hd_dst, "install.bat")
    # # end debug!
    copyprog.copytreeprog(hd_src, hd_dst)
    copyprog.copytreeprog(py_src, py_dst)

    # return file paths to new python exe, new install.bat launcher
    py = os.path.join(py_dst, "python.exe")
    bat = os.path.join(hd_dst, "install.bat")
    create_new_batfile(hd_dst, py, bat)
    return py, bat

def open_pbs_biotech():
    fp = "C:\\pbs\\builds\\PBS Windows Service\\PBS Biotech.exe"
    cmd3('"%s"'%fp, os.path.dirname(fp))

def exit_if_not(prompt, fn="<unknown>"):
    print(prompt)
    r = input("Enter 'y' to continue or any other key to exit")
    if r not in 'yY':
        raise ValueError("Something happened in %s"%fn)

def wait_for_hello(timeout=180):
    start = time.time()
    hwnd = 0
    while (time.time() - start) < timeout:
        hwnd = cursor.find_window(b"Hello - Google Chrome")
        if hwnd != 0:
            break
        time.sleep(1)
    if hwnd == 0:
        exit_if_not("Failed to find Hello - Verify Hello is Open.", "wait_for_hello")
    else:
        time.sleep(60)  # wait for hello to boot....

def confirm_rio_running():
    r = input("Confirm RIO is running or 'exit' to exit")
    if r.lower() == 'exit':
        raise SystemExit

state = 0
def main():
    global state
    if not check_admin():
        return
    state, data = check_state()
    if state == 0:
        print("Beginning setup. Press ctrl-c to quit at any time.")
    else:
        print("Resuming setup. Press ctrl-c to quit at any time.")
        
    if state == STATE_EXTRACT:
        name = get_computer_name()
        d, t = get_date_time()
        fldr = select_install_type()
        py, bat = extract_to_desktop()
        # sadmin_solidify(EXTRACT_DIR)
        set_state(STATE_INIT, (py, bat, name, d, t, fldr))
        restart_instance(py, bat)  # raises SystemExit
        return                     # Unreachable?
    if state == STATE_INIT:
        py, bat, name, d, t, fldr = data
        set_computer_name(name)
        set_date_time(d, t)
        maybe_handle_touchscreen()
        schedule_for_startup(py, bat)
        set_state(STATE_INSTALL_PBS, fldr)
        reboot()                   # raises SystemExit
        return                     # Unreachable?
    if state == STATE_INSTALL_PBS:
        fldr = data
        action = allow_bat()
        # batch files use working directory of caller
        # so chdir to ensure they use the right path
        here = os.path.abspath(".")
        os.chdir(fldr)
        install_certs(fldr)
        install_pbs.image_rio(fldr)
        run_recorder(fldr)
        disable_bat(action)
        os.chdir(here)

        # from here on below, a lot of user 
        # interaction is needed
        # below here untested!!!
        confirm_rio_running()
        open_pbs_biotech()
        wait_for_hello()
        uiactions.login_to_webui()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        msg = "Error installing. Press Enter to exit."
    else:
        msg = "Successfully installed. Press Enter to exit."
    input(msg)