import subprocess, sys, sleep
def cmd(c, check=True, shell=False, **kw):
    print("-"*30)
    print("CMD:", c)
    rv = subprocess.run(c, check=check, shell=shell, **kw)
    print("-"*30)
    return rv

def cmd2(c, shell=False, **kw):
    print("-"*30)
    print("CMD:", c)
    rv = subprocess.Popen(c, shell=shell, **kw)
    print("-"*30)
    return rv

CREATE_NEW_CONSOLE = 0x10

def cmd3(c, cwd, **kw):
    """ starts an independent process """
    cmd2(c, shell=False, stdin=None, stderr=None, stdout=None, close_fds=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|CREATE_NEW_CONSOLE, cwd=cwd, **kw)

def read_until(p, s):
    """ read subprocess's stdout until the string is found """
    if isinstance(s, str):
        s = s.encode('ascii')
    b = bytearray()
    l = len(s)
    f = p.stdout.read(l)
    b.extend(f)
    sys.stdout.write(f.decode())
    while b[-l:] != s:
        f = p.stdout.read(1)
        b.extend(f)
        sys.stdout.write(f.decode())
        sleep(0.5)
    return b

def read_until2(p,s):
    if isinstance(s, str):
        s = s.encode('ascii')
    b = bytearray()
    l = len(s)
    f = p.stdout.read(l)
    b.extend(f)
    sys.stdout.write(f.decode())
    while b[-l:] != s:
        f = p.stdout.read(1)
        b.extend(f)
        sys.stdout.write(f.decode())
        sleep(0.5)
        yield
    return b