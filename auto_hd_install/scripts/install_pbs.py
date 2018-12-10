import os, time
from subcmd import cmd2, subprocess, read_until, read_until2
from send_input import send_input
import regions, cursor

class SelectCancel(Exception):
    pass

def select(l, prompt):
    print()
    print(prompt)
    for i, d in enumerate(l):
        print("%-3d: %s"%(i,d))
    while True:
        i = input("Enter selection (or 'q' to quit): ")
        if i == 'q':
            raise SelectCancel
        try:
            n = int(i)
            s = l[n]
        except Exception:
            print("%r is not a valid selection."%i)
            continue
        return s

def _sort_types(s):
    """ Sort 'Mag' before 'Air' bioreactors """
    s = s.lower()
    parts = s.split()
    am = parts[0]
    if am not in ("mag", "air"):
        return (2, am, 0, 0)
    sz = parts[1]
    date = parts[-1]
    if am.startswith("mag"):
        i = 0
    elif am.startswith("air"):
        i = 1
    return (i, am, int(sz), date)    

def _filter(files):
    rv = []
    for f in files:
        if f[:3].lower() not in ("mag", "air"):
            continue
        rv.append(f)
    return rv

def choose_config(fp):
    return select(sorted(_filter(os.listdir(fp)), key=_sort_types), "Select Bioreactor Type")


def _findf(d,fn):
    f = None
    found = False
    for f in os.listdir(d):
        if fn in f:
            found = True
            break
    if not found or f is None:
        raise FileNotFoundError("Failed to find %r"%fn)
    return f


def image_rio(d):
    """ Simplified image_rio function that just
    runs RIO installer and exits when done. 
    Todo is to use mouseclicks/sikuli to automate
    password generation here. 
    """
    fp = os.path.join(d, _findf(d, "install.bat"))
    p = cmd2(fp, shell=True, stdout=subprocess.PIPE)
    read_until(p, b"Press any key to continue . . .")
    send_input(b"\r\n")

# def image_rio(d):
#     fp = os.path.join(d, _findf(d, "install.bat"))
#     p = cmd2(fp, shell=True, stdout=subprocess.PIPE)
#     title = b"Create An Encryption File.vi"
#     reader = read_until2(p, b"Press any key to continue . . .")

#     # read text for user while waiting for encryption VI...
#     while not cursor.find_window(title):
#         time.sleep(1)
#         next(reader, None)

#     # run the encryption VI
#     # use hard coded wait timers
#     # to ensure everything works
#     time.sleep(10)  # wait for window to open properly
#     regions.AUTH_SBRIO_PASSWORD.click()
#     time.sleep(3)
#     regions.AUTH_SBRIO_RUN.click()

#     while True:
#         try:
#             next(reader)
#         except StopIteration:
#             break
#         except Exception:
#             raise
#     send_input(b"\r")