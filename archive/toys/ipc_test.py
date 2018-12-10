"""

Created by: Nathan Starkweather
Created on: 03/29/2016
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import logging
import sys
del sys.path[0]

logger = logging.getLogger(__name__)
_h = logging.StreamHandler()
_f = logging.Formatter("%(created)s %(name)s %(levelname)s (%(lineno)s): %(message)s")
_h.setFormatter(_f)
logger.addHandler(_h)
logger.propagate = False
logger.setLevel(logging.DEBUG)
del _h, _f


def sock_client(address, sz):
    import sys
    s = socket.socket()
    s.settimeout(1)
    _time = time.time
    total = mb_sec = 0
    nreads = 0
    write = sys.stdout.write
    try:
        s.connect(address)
    except OSError:
        print(address)
        raise
    start = time.time()
    try:
        while not _time() - start: pass
        while True:
            msg = s.recv(sz)
            if not msg:
                break
            nreads += 1
            total += len(msg)
            if not nreads % 5000:
                dt = (_time() - start)
                byte_sec = total / dt
                mb_sec = byte_sec / 1024 / 1024
                gb_sent = total / 1024 / 1024 / 1024
                kwrites_sec = nreads / dt / 1000
                write("\rBufsz: %d %.2f GB read %.2f mb/sec %dk reads/sec" % (sz, gb_sent, mb_sec, kwrites_sec))
    except socket.timeout:
        pass
    except Exception:
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(0)

    dt = (_time() - start - 1)  # -1 for timeout
    byte_sec = total / dt
    mb_sec = byte_sec / 1024 / 1024
    gb_sent = total / 1024 / 1024 / 1024
    kwrites_sec = nreads / dt / 1000
    write("\rBufsz: %d %.2f GB read %.2f mb/sec %dk reads/sec" % (sz, gb_sent, mb_sec, kwrites_sec))
    print("")
    # print("Final: %.2f MB/sec" % mb_sec)


import random
import time
import sys


def sock_server(s, sz, test_length=15):
    msg = bytes(bytearray(random.randint(1, 254) for _ in range(sz)))
    total = mb_sec = 0
    _time = time.time
    start = _time()
    while not _time() - start: pass
    write = sys.stdout.write
    end = start + test_length
    _len = len(msg)
    nwrites = 0
    while _time() < end:
        s.sendall(msg)
        total += _len
        nwrites += 1
        # if not nwrites % 50000:
        #     dt = (_time() - start)
        #     byte_sec = total / dt
        #     mb_sec = byte_sec / 1024 / 1024
        #     gb_sent = total / 1024 / 1024 / 1024
        #     kwrites_sec = nwrites / dt / 1000
        #     write("\r%.2f GB sent %.2f mb/sec %dk writes/sec" % (gb_sent, mb_sec, kwrites_sec))
    return mb_sec


import multiprocessing


def main():

    serv = socket.socket()
    serv.bind(("localhost", 0))
    addr = serv.getsockname()
    serv.listen(1)
    test_length = 10
    print("TCP ICP throughput: %d second test" % test_length)
    for shift in range(16, 17):
        sz = 1 << shift
        p = multiprocessing.Process(None, sock_client, "Echo Client", (addr, sz))
        p.daemon = True
        p.start()
        s, _ = serv.accept()
        mb_sec = sock_server(s, sz, test_length)
        # print("Joining")
        p.join()
        # print("")
        # print("Final: %.2f MB/sec" % mb_sec)


from scripts.archive.toys.wrappers import ntfile, namedpipe
import ctypes


class NamedPipe():
    def __init__(self):
        self.name = None
        self._handle = None

    def _translate_name(self, name):
        pipestart = "\\\\.\\pipe\\"
        if not name.startswith(pipestart):
            name = pipestart + name
        return name

    def close(self):
        if self._handle:
            try:
                ctypes.windll.kernel32.CloseHandle(self._handle)
            except ctypes.ArgumentError:
                raise
            self._handle = None

    def _checkhandle(self):
        if self._handle is None:
            raise ValueError("Invalid operation on empty handle")

    def write(self, msg):
        if not isinstance(msg, bytes):
            raise TypeError(type(msg))
        ntfile.WriteFile(self._handle, msg)

    def read(self, n=1024):
        return ntfile.ReadFile(self._handle, n)

    def __del__(self, *args):
        self.close()


class PipeServer(NamedPipe):
    _DEFAULT_INBUF = _DEFAULT_OUTBUF = 65536

    def __init__(self, open_mode=namedpipe.DEFAULT_OPENMODE,
                 pipe_mode=namedpipe.DEFAULT_PIPEMODE, max_instances=1, timeout=0):
        super().__init__()
        self.pipe_mode = pipe_mode
        self.max_instances = max_instances
        self.timeout = timeout
        self.open_mode = open_mode

    def bind(self, name):
        self.name = self._translate_name(name)
        self._handle = namedpipe.CreateNamedPipe(self.name.encode('ascii'), self.open_mode,
                                                 self.pipe_mode, self.max_instances,
                                                 self._DEFAULT_OUTBUF, self._DEFAULT_INBUF,
                                                 self.timeout, None)


class PipeClient(NamedPipe):
    def __init__(self, name=None, access=ntfile.GENERIC_READ | ntfile.GENERIC_WRITE,
                 open_mode=ntfile.OPEN_EXISTING):
        super().__init__()
        self.open_mode = open_mode
        self.name = name
        self.access = access
        if self.name:
            self.name = self._translate_name(self.name)
            self.connect(self.name)

    def connect(self, name):
        self.name = self._translate_name(name)
        self._handle = ntfile.CreateFile(self.name.encode('ascii'), self.access, 0, None, self.open_mode, 0, None)


def random_name(length=8):
    import string
    import random
    chars = string.ascii_uppercase+string.ascii_lowercase+string.digits
    name = ''.join(random.SystemRandom().choice(chars) for _ in range(length))
    return name

def pipe():
    name = None


def lineno():
    import inspect
    return inspect.currentframe().f_back.f_lineno

def main2():
    print(lineno())
    p = PipeServer()
    print(lineno())
    p.bind("foo")
    print(lineno())
    p2 = PipeClient()
    p2.connect("foo")
    for _ in range(100):
        p.write(("Hello World! %d" % _).encode('ascii'))
        print(p2.read())


if __name__ == '__main__':
    import socket
    main2()


