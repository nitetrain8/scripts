"""

Created by: Nathan Starkweather
Created on: 03/05/2016
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import logging
import matplotlib.pyplot as pyplot
import matplotlib.figure
import collections
import multiprocessing
import tkinter
import numpy as np
import math
from time import time
from select import select
import socket
import queue
import threading
import io

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)


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
    step = 2 * np.pi / period
    while True:
        y = math.sin(x)
        yield x, y
        x += step


class SimpleRTPlot():
    """ Simple interface to a real-time plot based on matplotlib.
    Intended primarily as a learning tool to understand the basics of matplotlib.
    Extensive comments may be used as a result.
    """

    def __init__(self, x_data=(), y_data=(), max_pts=None, style='ggplot'):

        # plots expect data to be np arrays
        # but np arrays can't be appended to
        # resulting in O(n^2) behavior
        # so store data python objects instead.

        # deque is used to more easily and efficiently
        # work with arbitrary limits on the total number
        # of data points

        # data is stored in separate containers for x and y
        # data, because that's how the plotting interface
        # works.

        self.x_data = collections.deque(x_data, max_pts)
        self.y_data = collections.deque(y_data, max_pts)
        self.style = style
        self.max_pts = max_pts
        self.proc = None

    def show(self):
        args = [self.max_pts, self.style]
        p = multiprocessing.Process(None, launch_plot, "RTPlot", args)
        p.daemon = True
        p.start()
        self.proc = p

    def visible(self):
        return self.proc and self.proc.is_alive()


class SimpleRTPlotProcess():
    def __init__(self, func, max_pts, style):
        self.x_data = collections.deque((), max_pts)
        self.y_data = collections.deque((), max_pts)
        self.max_pts = max_pts
        self.style = style
        self.func = func
        self.figure = None
        self.subplot = None
        self.background = None
        self.line = None

    def clear_pyplot(self):
        pyplot.close(self.figure)
        self.figure = None
        self.subplot = None
        self.background = None
        self.line = None

    def setup_pyplot(self):
        pyplot.style.use(self.style)

        num = None
        figsize = None
        dpi = None
        facecolor = None
        edgecolor = None
        frameon = True
        fig_klass = matplotlib.figure.Figure

        self.figure = pyplot.figure(num, figsize, dpi, facecolor, edgecolor, frameon, fig_klass)
        self.subplot = self.figure.add_subplot(1, 1, 1)
        self.line, = self.subplot.plot(self.x_data, self.y_data)
        self.background = self.figure.canvas.copy_from_bbox(self.subplot.bbox)
        self.fps_txt = self.subplot.text(0.01, 0.95, 'FPS:', transform=self.subplot.transAxes)
        self.npts_txt = self.subplot.text(0.01, 0.92, "Data Points:", transform=self.subplot.transAxes)
        self.debug_txt = self.subplot.text(0.01, 0.89, "", transform=self.subplot.transAxes)

    def show(self):
        self.setup_pyplot()
        self.figure.show()
        try:
            self._mainloop()
        except tkinter.TclError:
            # user hit 'X' button and tkinter freaked out when we tried to re-blit
            pass
        finally:
            self.clear_pyplot()

    def _mainloop(self):
        frames = 0
        start = time()
        while True:
            self.subplot.relim()
            self.subplot.autoscale_view(True, True, True)
            x, y = self.func()
            self.x_data.append(x)
            self.y_data.append(y)
            self.line.set_data(self.x_data, self.y_data)
            self.figure.canvas.restore_region(self.background)
            self.figure.draw_artist(self.subplot)

            fps_txt.set_text("FPS:%.1f" % (frames / ((time() - start)or 1)))
            npts_txt.set_text("Data Points:%d" % len(self.x_data))

            self.figure.canvas.blit(self.subplot.bbox)
            self.figure.canvas.flush_events()
            frames += 1


class SocketRTPlot(SimpleRTPlot):

    default_cfg = {
        'local_addr': ('localhost', 12345),
        'remote_addr': ('localhost', 12346)
    }

    def __init__(self, local_addr=None, remote_addr=None, max_pts=100, style='ggplot', max_qsize=1000):

        self.local_addr = local_addr or self.default_cfg['local_addr']
        self.remote_addr = remote_addr or self.default_cfg['remote_addr']
        self.producer = None
        self.shutdown_event = None
        self.producer_queue = None
        self.max_qsize = max_qsize
        super().__init__((), (), max_pts, style)

    def show(self):

        self._launch_process()
        self._launch_producer_thread()

    def _launch_producer_thread(self):
        # set up local producer queue

        producer_queue = queue.Queue(self.max_qsize)
        shutdown_event = threading.Event()
        args = self.local_addr, self.remote_addr, producer_queue, shutdown_event, SimpleRTPlotProto, float
        producer = threading.Thread(None, _rt_plot_socket_producer, "SocketRTPlot Producer Thread", args)
        producer.daemon = True
        producer.start()
        self.producer = producer
        self.shutdown_event = shutdown_event
        self.producer_queue = producer_queue

    def _launch_process(self):
        host, port = self.remote_addr
        args = (
            host,
            port,
            self.max_pts,
            self.style,
            self.max_qsize
        )
        p = multiprocessing.Process(None, launch_socket_plot, "SocketRTPlot Plotter Process", args)
        p.daemon = True
        p.start()
        self.proc = p

    def add_data(self, x, y):
        self.producer_queue.put((x, y))


class SocketRTPlotProcess(SimpleRTPlotProcess):
    def __init__(self, host, port, max_pts=100, style='ggplot', max_qsize=1000):
        self.host = host
        self.port = port
        self.max_qsize = max_qsize
        super().__init__(None, max_pts, style)

    def show(self):
        self.setup_pyplot()
        self._launch_consumer_thread()
        try:
            self._mainloop()
        except tkinter.TclError:
            pass

    def _launch_consumer_thread(self):
        consumer_queue = queue.Queue(self.max_qsize)
        args = self.host, self.port, consumer_queue, SimpleRTPlotProto, float
        consumer = threading.Thread(None, _rt_plot_socket_consumer, "SocketRTPlotProcess Consumer Thread", args)
        consumer.daemon = True
        consumer.start()
        self.consumer = consumer
        self.consumer_queue = consumer_queue

    def _read_queue(self):
        """
        Drain the consumer queue, based on approximate length at
        the time this function is called. This prevents stalling
        as a result of the consumer queue growing too quickly.

        :return: bool indicating whether data updates occurred.
        """
        sz = self.consumer_queue.qsize()
        if not sz:
            self.debug_txt.set_text("Queue empty")
            return False

        for nread in range(sz):
            try:
                x, y = self.consumer_queue.get(False)
            except queue.Empty:
                # shouldn't happen, since we're the only consumer
                logger.debug("queue.Empty exception reading queue")
                break
            else:
                self.x_data.append(x)
                self.y_data.append(y)
        self.debug_txt.set_text("Queue len: %s Read: %d" % (sz, nread + 1))
        return True

    def _mainloop(self):
        self.figure.show()
        self.background = self.figure.canvas.copy_from_bbox(self.subplot.bbox)
        frames = 0
        start = time()
        while True:
            update = self._read_queue()
            if frames > 100:
                update = False
            if update:
                logger.debug("Got Update: x:%.2f y:%.2f" % (self.x_data[-1], self.y_data[-1]))
                self.line.set_data(self.x_data, self.y_data)
                self.subplot.relim()
                self.subplot.autoscale_view(True, True, True)
                self.figure.canvas.restore_region(self.background)
                self.figure.draw_artist(self.subplot)
            else:
                self.figure.canvas.restore_region(self.background)
                self.figure.draw_artist(self.fps_txt)
                self.figure.draw_artist(self.npts_txt)
                self.figure.draw_artist(self.debug_txt)

            self.fps_txt.set_text("FPS:%.1f" % (frames / ((time() - start) or 1)))
            self.npts_txt.set_text("Data Points:%d" % len(self.x_data))

            self.figure.canvas.blit(self.subplot.bbox)
            self.figure.canvas.flush_events()
            frames += 1


class SocketPlotterTest(SocketRTPlotProcess):

    def _read_queue(self):
        if self.func is None:
            self.func = sin_wave(50)
        return self.func()


class SimpleRTPlotProto():
    def __init__(self, conv_type=float):
        self.conv = conv_type

    def write_msg(self, x, y):
        return ("%s;%s\n" % (x, y)).encode('ascii')

    def write_lst(self, data):
        if not data:
            return b''
        buf = io.StringIO()
        for x, y in data:
            buf.write("%s;%s\n" % (x, y))
        return buf.getvalue().encode('ascii')

    def decode_msg(self, line):
        str_x, str_y = line.decode('ascii').split(";")
        try:
            return self.conv(str_x), self.conv(str_y)
        except ValueError:
            logger.exception("Could not convert message to %s" % self.conv.__name__)


class _StopServing(Exception):
    def __init__(self, restart=True):
        self.restart = restart
        self.args = self.__class__.__name__,


def _rt_plot_socket_consumer(host, port, q, proto_klass=SimpleRTPlotProto, dtype=float):
    assert isinstance(q, queue.Queue)
    proto = proto_klass(dtype)

    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, port))
        retry = _socket_reader_serve(sock, proto, q)
        if not retry:
            sock.close()
            return


def _socket_reader_serve(sock, proto, q):
    rfile = sock.makefile("rb")
    while True:
        try:
            line = rfile.readline()
        except Exception:
            logger.exception("Readline failed")
            return True
        if line == b'shutdown\n':
            sock.close()
            return False
        res = proto.decode_msg(line)
        if res is not None:
            q.put(res, True, None)


def _rt_plot_socket_producer(local_addr, remote_addr, q, shutdown, proto_klass=SimpleRTPlotProto, dtype=float):
    assert isinstance(q, queue.Queue)
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(local_addr)
    proto = proto_klass(dtype)
    while True:
        if shutdown.is_set():
            server.close()
            return
        retry = _socket_writer_serve(server, remote_addr, shutdown, proto, q)
        if not retry:
            server.close()
            return


def sendall_to(server, msg, addr):
    while msg:
        try:
            n = server.sendto(msg, addr)
        except OSError:
            raise
        msg = msg[n:]


def _socket_writer_serve(server, address, shutdown, proto, q):
    assert isinstance(server, socket.socket)
    while True:
        if shutdown.is_set():
            shtdwn_msg = b"shutdown\n"
            sendall_to(server, shtdwn_msg, address)
            server.close()
            return False
        data = _socket_writer_queue_empty(q)
        msg = proto.write_lst(data)
        try:
            sendall_to(server, msg, address)
        except Exception:
            logger.exception("Sendall failed")
            return True


def _socket_writer_queue_empty(q):
    sz = q.qsize()
    sz = min(sz, 100)
    rv = []
    for _ in range(sz):
        try:
            x, y = q.get(False)
        except queue.Empty:
            break
        else:
            rv.append((x, y))
    return rv


def launch_plot(max_pts, style):
    func = sin_wave(max_pts / 2)
    plot = SimpleRTPlotProcess(func, max_pts, style)
    plot.show()


def launch_socket_plot(host, port, max_pts, style, max_qsize):
    # host, port, max_pts, style = plot_args
    plot = SocketRTPlotProcess(host, port, max_pts, style, max_qsize)
    plot.show()


def main():
    import sys

    plot = SimpleRTPlot((), (), 100)
    plot.show()
    # from time import time, sleep
    # start = time()
    # end = start + 10
    # while time() < end:
    #     print("\r%d seconds left:" % int(end - time()), end="")
    #     sleep(0.5)
    #     if not plot.visible():
    #         print("")
    #         print("Super major error: subprocess died :-(")
    #         break
    plot.proc.join()

from time import sleep


@nextroutine
def random(min=1, max=100):
    from random import randint
    x = 0
    while True:
        yield x, randint(min, max)
        x += 1


def _main2_test_producer(period, plot, interval):
    generator = sin_wave(period)
    # generator = random(1, 100)
    while True:
        x, y = generator()
        plot.add_data(x, y)

        if interval and interval > 0:
            sleep(interval)


def main2():
    # plot = SocketPlotterTest('localhost', 12345)
    plot = SocketRTPlot()
    plot.show()
    period = 50
    interval = 0.0

    t = threading.Thread(None, _main2_test_producer, "TestProducer", (period, plot, interval))
    t.daemon = True
    t.start()

    from time import time, sleep
    start = time()
    end = start + 1000
    while time() < end:
        print(plot.producer_queue.qsize())
        print("\r%d seconds left:" % int(end - time()), end="")
        sleep(0.5)
        if not plot.visible():
            print("")
            print("Super major error: subprocess died :-(")
            break

if __name__ == '__main__' and 'get_ipython' not in globals():
    main2()
    import multiprocessing.managers
    multiprocessing.managers
