"""

Created by: Nathan Starkweather
Created on: 03/04/2016
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import logging

logger = logging.getLogger(__name__)

import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.animation as anim
import numpy as np


def main():
    f = plt.figure()
    ax = f.add_subplot(1, 1, 1)
    x_data = np.arange(2*np.pi, step=2*np.pi / 100)
    sin_arg = x_data
    print(sin_arg)
    y_data = np.sin(sin_arg)
    line = ax.plot(x_data, y_data)[0]
    # f.show()
    i = 0
    # plt.show(False)
    # plt.draw()
    bkgd = f.canvas.copy_from_bbox(ax.bbox)
    from time import sleep, time
    f.show()
    start = time()
    for i in range(1000):
        x = x_data * i / 2
        y = np.sin(x)
        # print(x)
        line.set_data(x_data, y)
        f.canvas.restore_region(bkgd)
        f.draw_artist(ax)
        f.canvas.blit(ax.bbox)
        f.canvas.flush_events()
    end = time()
    print("FPS: %s" % (1000 / (end - start)))
from math import sin

import itertools

def iterdata():
    step = np.pi / 100
    xi = itertools.cycle(i * step for i in range(1000))
    while True:
        x = next(xi)
        y = sin(x)
        yield x, y


import collections
import threading
from time import sleep


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

        x_data = collections.deque(x_data, max_pts)
        y_data = collections.deque(y_data, max_pts)

        self.x_data = x_data
        self.y_data = y_data
        self.max_pts = max_pts
        self.style = style

        self.clear_pyplot()

        self.data_lock = threading.RLock()
        self.pyplot_lock = threading.RLock()
        self.setup_complete = threading.Event()
        self.shutdown_complete = threading.Event()
        self.new_data = False
        self.stop_loop = False
        self.plot_thread = None
        self._init()

    def _init(self):
        self.thread_target = self.threadloop

    def clear_pyplot(self):
        self.figure = None
        self.subplot = None
        self.background = None
        self.line = None

    def setup_pyplot(self):
        plt.style.use(self.style)

        num = None
        figsize = None
        dpi = None
        facecolor = None
        edgecolor = None
        frameon = True
        fig_klass = matplotlib.figure.Figure

        # self.figure = plt.figure(num, figsize, dpi, facecolor, edgecolor, frameon, fig_klass)
        self.figure = plt.figure()
        self.subplot = self.figure.add_subplot(1, 1, 1)
        self.line, = self.subplot.plot(self.x_data, self.y_data)
        self.background = self.figure.canvas.copy_from_bbox(self.subplot.bbox)
        self.figure.show()
        # self.figure.draw()

    def show(self):
        self.clear_pyplot()
        self.setup_complete.clear()
        self.shutdown_complete.clear()

        self.plot_thread = threading.Thread(None, self.thread_target, daemon=True)
        self.plot_thread.start()
        self.setup_complete.wait()

    def add_data(self, x, y):
        with self.data_lock:
            self.x_data.append(x)
            self.y_data.append(y)
            self.notify_new_data()

    def notify_new_data(self):
        self.new_data = True

    def stop(self):
        self._shutdown_loop()
        self.shutdown_complete.wait()
        self.shutdown_complete.clear()
        self.setup_complete.clear()

    def _shutdown_loop(self):
        self.stop_loop = True
        self.plot_thread.join()
        self.plot_thread = None

    def extend_data(self, x_data, y_data):
        if len(x_data) != len(y_data):
            raise ValueError("Data must have same length!")
        with self.data_lock:
            self.x_data.extend(x_data)
            self.y_data.extend(y_data)
            self.notify_new_data()

    def threadloop(self):
        self.setup_pyplot()
        self.setup_complete.set()
        while not self.stop_loop:
            with self.data_lock:
                if self.new_data:
                    with self.pyplot_lock:
                        self.new_data = False
                        self.line.set_data(self.x_data, self.y_data)
                        self.figure.canvas.restore_region(self.background)
                        self.figure.draw_artist(self.subplot)
                        self.figure.canvas.blit(self.subplot.bbox)
                        self.subplot.autoscale_view()
            self.figure.canvas.flush_events()
            sleep(0.01)
        self.clear_pyplot()
        self.shutdown_complete.set()


class SimpleRTPlot2(SimpleRTPlot):

    def _init(self):
        self.thread_target = self._threadloop2

    def notify_new_data(self):
        self.figure.canvas.stop_event_loop()

    def _shutdown_loop(self):
        self.stop_loop = True
        self.figure.canvas.stop_event_loop()
        self.plot_thread.join()
        self.plot_thread = None

    def _threadloop2(self):
        self.setup_pyplot()
        # start with event loop running
        self.figure.canvas.start_event_loop(1)

        while not self.stop_loop:
            with self.data_lock:
                self.line.set_data(self.x_data, self.y_data)
                with self.pyplot_lock:
                    self.figure.canvas.restore_region(self.background)
                    self.figure.draw_artist(self.subplot)
                    self.figure.canvas.blit(self.subplot.bbox)
                    self.subplot.autoscale_view()
            self.figure.canvas.start_event_loop(1)
        self.clear_pyplot()


from tkinter import TclError
from time import time


class SimpleRTPlot3(SimpleRTPlot):
    def show(self):
        self.setup_pyplot()
        self.last_update = time()
        def flush(flushfunc):
            while True:
                flushfunc()
        threading.Thread(None, flush, None, (self.figure.canvas.flush_events,), daemon=True).start()

    def notify_new_data(self):
        self.line.set_data(self.x_data, self.y_data)
        self.figure.canvas.restore_region(self.background)
        self.figure.draw_artist(self.subplot)
        try:
            self.figure.canvas.blit(self.subplot.bbox)
        except TclError:
            return
        # if time() - self.last_update > 1:
        #     self.figure.canvas.flush_events()
        #     self.last_update = time()


def main2():

    plot = SimpleRTPlot3(max_pts=20)
    data = iterdata()
    plot.show()
    plot.subplot.set_ylim(-1, 1, True)
    plot.subplot.set_xlim(0, np.pi * 5, True)
    frames = 0
    start = time()
    while True:
        x, y = next(data)
        plot.add_data(x, y)
        frames += 1
        print("\rFPS: %s" % (frames / (time() - start)), end="")



if __name__ == '__main__':
    # main2()
    pass
