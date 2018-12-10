"""

Created by: Nathan Starkweather
Created on: 03/12/2016
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import logging

logger = logging.getLogger(__name__)
_h = logging.StreamHandler()
_f = logging.Formatter("%(created)s %(name)s %(levelname)s (%(lineno)s): %(message)s")
_h.setFormatter(_f)
logger.addHandler(_h)
logger.propagate = False
logger.setLevel(logging.DEBUG)
del _h, _f


def run_example(t):
    import socket, sys

    recvbuff = bytearray(16)
    recvview = memoryview(recvbuff)

    size = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    s.settimeout(1)
    nbytes = 1
    while True:
        if not nbytes or not t.is_alive():
            break
        try:
            nbytes = s.recv_into(recvview)
        except socket.timeout:
            continue
        size += nbytes
        recvview = recvview[nbytes:]
        if not len(recvview):
            print("filled a chunk", recvbuff)
            recvview = memoryview(recvbuff)
        s.send(recvview.tobytes()[::-1])
    print('end of data', recvbuff[:len(recvview)], size)

    s.close()


def server(addr):
    import socket
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    con, addr = s.accept()
    while True:
        con.send(b"hello world" * 100)
        con.recv(4096)

if __name__ == '__main__':
    import threading

    HOST = 'localhost'  # The remote host
    PORT = 50008  # The same port as used by the server
    addr = (HOST, PORT)
    t = threading.Thread(None, server, None, (addr,))
    t.daemon = True
    t.start()
    run_example(t)
