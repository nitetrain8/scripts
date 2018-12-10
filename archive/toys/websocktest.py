"""

Created by: Nathan Starkweather
Created on: 03/30/2016
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import logging
import websockets
import asyncio

logger = logging.getLogger(__name__)
_h = logging.StreamHandler()
_f = logging.Formatter("%(created)s %(name)s %(levelname)s (%(lineno)s): %(message)s")
_h.setFormatter(_f)
logger.addHandler(_h)
logger.propagate = False
logger.setLevel(logging.DEBUG)
del _h, _f

def getloop():
    loop = asyncio.get_event_loop()
    return loop

def create_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop

create_loop()


@asyncio.coroutine
def ws_read(ws):
    msg = yield from ws.recv()
    return msg


@asyncio.coroutine
def client():
    loop = getloop()
    c = yield from websockets.connect("ws://localhost:12345")
    while True:
        msg = yield from ws_read(c)
        print("GOT MSG:", msg)


@asyncio.coroutine
def handler(ws, path):
    i = 1
    while True:
        yield from ws.send("Hello World! #%d" % i)
        yield from asyncio.sleep(1)
        i += 1


def start_server():
    loop = getloop()
    s = websockets.serve(handler, "localhost", 12345)
    s = loop.run_until_complete(s)
    return s


def main():
    s = start_server()
    c = client()
    getloop().run_until_complete(c)

if __name__ == '__main__':
    main()
