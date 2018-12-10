import subprocess, sys
def cmd(c, check=True, shell=False, **kw):
    print(c)
    return subprocess.run(c, check=check, shell=shell, **kw)

def cmd2(c, shell=False, **kw):
    print(c)
    return subprocess.Popen(c, shell=shell, **kw)

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
    return b