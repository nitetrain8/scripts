from hello import hello, hello3
import threading, queue
from ssl import SSLError
from requests.exceptions import RequestException
from scripts import wlan
import time
def worker(iq, oq, v):
    while True:
        ip = iq.get()
        if ip is None:
            return
        h = ping2(v, ip)
        if isinstance(h, int):
            if h >= 0:
                continue
            else:
                oq.put("Error scanning %s"%ip)
        else:
            s = found(h, ip)
            oq.put(s)
        iq.task_done()

def _ping(v, ip):
    if v == 2:
        AppClass = hello.HelloApp
    elif v == 3:
        AppClass = hello3.HelloApp
    else:
        raise ValueError(v)
    return AppClass(ip, timeout=1)

def ping2(v, ip):
    try:
        h = _ping(v, ip)
    except Exception:
        return 0
    try:
        return h.reactorname()
    except (SSLError, RequestException):
        return 1
    except Exception:
        return -1


def ping(v, ip):
    try:
        h = _ping(v, ip)
    except Exception:
        return None
    try:
        return h.reactorname()
    except Exception:
        print("Error scanning")
        return None
    
def found(h, ip):
    return "Found: %s at %s" % (h, ip)

def scan_all(v=2):
    ipt = "192.168.1.%d"
    for i in range(2, 100):
        ip = ipt%i
        print("\rScanning %s ...  "%ip, end="")
        h = ping(v, ip)
        if h:
            print(found(h, ip))
            
def display(oq, verbose):
    while True:
        try:
            s = oq.get(False)
        except queue.Empty:
            return
        else:
            show(s, __verbose=verbose)
           

def show(*args, __verbose=True, **kw):
    if __verbose:
        print(*args, **kw)
        
def scan_mt(v=2, threads=8, verbose=True, pmin=2, pmax=100):
    global __v
    nw = wlan.get_current_wifi()
    if nw != 'pbstech':
        wlan.ensure_wifi('pbstech')
    time.sleep(3)
    
    tl = set()
    iq = queue.Queue()
    oq = queue.Queue()
    for i in range(threads):
        t = threading.Thread(None, worker, args=(iq, oq, v), daemon=True)
        t.start()
        tl.add(t)
    for i in range(pmin, pmax):
        ip = "192.168.1.%d"%i
        iq.put(ip)
    for i in range(threads):
        iq.put(None)  # sentinel
    while True:
        if iq.qsize() == 0:
            break
        else:
            display(oq, verbose)
    display(oq, verbose)
    if nw != 'pbstech':
        wlan.ensure_wifi(nw)
    show("Finished scanning", __verbose=verbose)
    
    
def usage():
    print("hello_ping [version=2] [threads=8] [verbose=True] [min_port=1] [max_port=100]")


if __name__ == "__main__":
    def main():
        v = 2
        threads = 8
        verbose = 'true'
        pmin = 1
        pmax = 100
        usage()
        line = input("Enter CMD: ")
        
        def op(i, default, f=str):
            try:
                v = ops[i]
            except IndexError:
                v = default
            return f(v)

        ops = line.split()
        v       = op(0, v, int)
        threads = op(1,threads, int)
        verbose = op(2, verbose, lambda s: s.lower() == "true")
        pmin    = op(3, pmin, int)
        pmax    = op(4, pmax, int)
        
        scan_mt(v, threads, verbose, pmin, pmax)
    while 1: 
        try:
            main()
        except Exception:
            import traceback
            traceback.print_exc()
            input()
            break