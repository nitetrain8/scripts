"""

Created by: Nathan Starkweather
Created on: 03/06/2016
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import logging
import math

from simplertplot.src import simplertplot

logger = logging.getLogger(__name__)
logger.addHandler(simplertplot._logger_handler)


def nextroutine(f):
    import functools

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        g = f(*args, **kwargs)
        return g.__next__
    return wrapped


@nextroutine
def sin_wave(period):
    x = 0
    step = 2 * math.pi / period
    while True:
        y = math.sin(x)
        yield x, y
        x += step


def dummy_producer(addr, interval=0):
    gen = sin_wave(50)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    proto = simplertplot.src.simplertplot.interproc.tcp_connection.session.SimpleRTProto()
    while True:
        x, y = gen()
        msg = proto.write_xy(x, y)
        sock.sendto(msg, addr)
        if interval and interval > 0:
            sleep(interval)


def main():
    addr = 'localhost', 12345
    plot = simplertplot.RTSocketProcess(addr, 1000, 'ggplot')
    producer = threading.Thread(None, dummy_producer, None, (addr, 0))
    producer.daemon = True
    producer.start()
    plot.show()


def main2():
    addr = 'localhost', 12345
    plot = simplertplot.RTSocketPlot(addr, 1000)
    plot.show()

from simplertplot.src.simplertplot import *


def main4():
    import yappi
    yappi.start()
    main2()
    stats = yappi.get_func_stats()
    stats.sort('ttot')
    stats.print_all()


def main5():
    import matplotlib.pyplot as plt
    fig = plt.figure()
    subplot = fig.add_subplot(1, 1, 1)
    x = 'fobar'
    y = 'barfoo'
    x_data = list(range(20))
    y_data = list(range(20))
    line, = subplot.plot(x_data, y_data)
    fig.show()
    line.set_data(x, y)
    fig.draw_artist(subplot)
    plt.draw()

if __name__ == '__main__':
    main5()
