"""

Created by: Nathan Starkweather
Created on: 03/05/2016
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import logging

logger = logging.getLogger(__name__)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
    p.add_argument('--sum', dest='accumulate', action='store_const', const=sum, default=max,
                   help='sum the integers (default: find the max)')
    rv = p.parse_args()
    print(rv.integers)
    print(rv.accumulate(rv.integers))


def worker(in_, out_):
    while True:
        msg = in_.get()
        print(msg)
        out_.put(msg[::-1])

def main3(fn, *args):
    fn(*args)


def producer(in_, out_):
    while True:
        msg = input("INPUT MSG: ")
        out_.put(msg)
        rsp = in_.get()
        print("GOT RSP:", rsp)


from time import sleep, time

def worker2(fn):
    i = 0
    start = time()
    while time() - start < 5:
        print("\r%d" % i, end="")
        i += 1
        sleep(.5)
        fn()

def main2():
    import multiprocessing
    import multiprocessing.queues
    import multiprocessing.context
    from concurrent.futures import process
    import concurrent.futures
    p = process.ProcessPoolExecutor(1)
    def fn():
        i = 0
        start = time()
        while time() - start < 5:
            print("\r%d" % i, end="")
            i += 1
            sleep(.5)
    import sys
    import math as mth, types
    sys.modules["__main__"] = types
    f= p.submit(mth.sin, (5,))
    assert isinstance(f, concurrent.futures.Future)
    def stop():
        raise Stop

    class Stop(Exception): pass
    f.add_done_callback(lambda f: stop)

    # while True:
    #     try:
    #         sleep(0.1)
    #     except Stop:
    #         break

import socket


def udp_1(q):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", 12345))
    data, addr = s.recvfrom(1)
    nsz = 1
    while True:
        msg = nsz * b"z"
        try:
            n = s.sendto(msg, addr)
            assert n == nsz
            print("\rSent %d bytes                    " % len(msg), end="")
            data = s.recv(nsz)
            assert len(data) == nsz
            nsz = grow(nsz)
        except OSError as e:
            q.put(e)
            raise


def grow(nsz, factor=1.05, state=[1, 1, 0]):
    # return int(nsz * factor // 1) + 1
    n, shift, num = state
    rv = n << shift
    if num % 2:
        state[1] = state[1] + 1
    state[2] = state[2] + 1
    # print(rv)
    if rv == 1<<16: rv -= 1000
    return rv


def udp_2(q):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = ("localhost", 12345)
    s.sendto(b"a", addr)
    nsz = n = 1
    while True:
        try:
            data = s.recv(nsz)
            assert len(data) == nsz, "%s != %s" % (len(data), n)
            n = s.sendto(b"a" * len(data), addr)
            assert n == len(data)
            nsz = grow(nsz)
        except OSError as e:
            q.put(e)
            raise


def main5():
    import threading
    import queue
    q = queue.Queue()
    t1 = threading.Thread(target=udp_1, args=(q,))
    t2 = threading.Thread(target=udp_2, args=(q,))
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()
    while True:
        if not t1.is_alive() or not t1.is_alive():
            break
    e = q.get()
    e


if __name__ == '__main__':
    main5()
