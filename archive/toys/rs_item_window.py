"""

Created by: Nathan Starkweather
Created on: 08/19/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import tkinter as tk
import tkinter.ttk as ttk
import time


_items = {
    "Irit",
    "Kwuarm",
    "Cadantine",
    "Ranarr"
}


class ItemEntry():
    def __init__(self, parent, name):
        self.label = ttk.Label(parent, text=name)
        self.entry = ttk.Entry(parent)

    def grid(self, row, col):
        self.label.grid(row=row, column=col, sticky=tk.E)
        self.entry.grid(row=row, column=col + 1, sticky=tk.E)


class ItemButton(ttk.Button):
    def __init__(self, master, name, cmd, **kw):
        self.tv = tk.StringVar(None, name)
        super().__init__(master, textvariable=self.tv, command=cmd, **kw)

    def grid(self, row, col, **kwargs):
        super().grid(row=row, column=col, **kwargs)


class StatefulItemButton(ItemButton):
    def __init__(self, master, name, initial_cmd):
        super().__init__(master, name, self._do_cmd)
        self._cmd = initial_cmd

    def _do_cmd(self, *args, **kwargs):
        self._cmd(*args, **kwargs)

    def set_cmd(self, cmd):
        self._cmd = cmd


class ItemFrame(ttk.Frame):
    def grid(self, row, col, **kwargs):
        super().grid(row=row, column=col, **kwargs)


class ItemLabelFrame(ttk.LabelFrame):
    def __init__(self, master, **kw):
        ttk.LabelFrame.__init__(self, master, **kw)

    def grid(self, row, col, **kwargs):
        super().grid(row=row, column=col, sticky=(tk.E, tk.W), columnspan=2, **kwargs)


class SlayerContextFrame(ItemLabelFrame):
    def __init__(self, master, name):
        super().__init__(master, text=name)
        self.cb_xp = cbxp = ItemEntry(self, "Combat XP:")
        self.slay_xp = slayxp = ItemEntry(self, "Slayer XP:")
        self.gp = gp = ItemEntry(self, "GP:")

        cbxp.grid(1, 1)
        slayxp.grid(2, 1)
        gp.grid(3, 1)


class SimpleLabel(ttk.Label):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)


class GenericContextFrame(ItemLabelFrame):
    def __init__(self, master, name):
        super().__init__(master, text=name)
        raise NotImplemented


class Timer():
    def _internal_reset(self):
        self._begin_time = 0
        self._end_time = 0
        self._paused = False
        self._pause_start = 0
        self._pause_total = 0
        self.stopped = True

    def __init__(self):
        self._internal_reset()

        # interfaces lag during "after" callbacks
        # localize some func references to minimize
        self.get_time = time.time

    def start(self):
        self._begin_time = self.get_time()
        self._pause_total = 0
        self.stopped = False

    def get_hms(self):
        if self.stopped:
            ct = self._end_time
        else:
            ct = self.get_time()

        diff = ct - self._begin_time - self._pause_total
        hrs = diff // 3600
        mins = diff // 60 % 60
        sec = diff - hrs * 3600 - mins * 60
        return hrs, mins, sec

    def end(self):
        if self.stopped:
            return
        self.stopped = True
        self._end_time = self.get_time()

    def format_hms(self):
        hrs, mins, sec = self.get_hms()
        return "%d:%.2d:%-2.1f" % (hrs, mins, sec)

    def pause(self, pause):
        if (pause and self._paused) or \
                (not pause and not self._paused):
            return
        elif pause:
            self._pause_begin = self.get_time()
            self._paused = True
            return
        else:
            self._pause_total += (self.get_time() - self._pause_begin)
            self._paused = False


class TimerState():
    TS_IDLE = 0
    TS_RUNNING = 1
    TS_PAUSED = 2


class TimerLabel():

    def __init__(self, master, name):
        self.frame = ttk.LabelFrame(master, text=name)
        self.tv = tk.StringVar(None, "00:00:00")
        self.name_label = ttk.Label(self.frame, textvariable=self.tv, font=16)
        self.timer = Timer()
        self.after_id = None
        self.state = TimerState.TS_IDLE

    def update(self):
        try:
            hms_string = self.timer.format_hms()
            self.tv.set(hms_string)
        finally:
            self.after_id = self.name_label.after(100, self.update)

    def start(self):
        if not self.state == TimerState.TS_IDLE:
            return
        self.after_id = self.name_label.after(100, self.update)
        self.timer.start()
        self.state = TimerState.TS_RUNNING

    def pause(self):
        if self.timer.stopped:
            return
        self.name_label.after_cancel(self.after_id)
        self.timer.pause(True)
        self.state = TimerState.TS_PAUSED

    def resume(self):
        if not self.state == TimerState.TS_PAUSED:
            return
        self.timer.pause(False)
        self.state = TimerState.TS_RUNNING
        self.name_label.after(100, self.update)

    def stop(self):
        self.timer.end()
        self.name_label.after_cancel(self.after_id)

    def grid(self, row, col, **kw):
        self.name_label.grid()
        self.frame.grid(row=row, column=col, rowspan=2, **kw)


class ItemWindow():
    def __init__(self):
        self.root = root = tk.Tk()

        self.inner_frame = inner_frame = ItemFrame(root)
        inner_frame.grid(0, 0, columnspan=6)

        self.taskname_item = tni = ItemEntry(inner_frame, "Taskname:")
        self.taskamt_item = tai = ItemEntry(inner_frame, "Amount")
        self.task_timer = ttl = TimerLabel(inner_frame, "Task Timer:")

        tni.grid(1, 1)
        tai.grid(2, 1)
        ttl.grid(1, 3)

        self.begin_info = SlayerContextFrame(inner_frame, "Beginning Info:")
        self.begin_info.grid(3, 1)
        self.end_info = SlayerContextFrame(inner_frame, "End Info:")
        self.end_info.grid(3, 3)

        self.vars = vars = []
        res = ttk.Label(inner_frame, text="Herb Resources:")
        res.grid(row=4, column=1, pady=5)

        for i, it in enumerate(_items, 5):
            e = ItemEntry(inner_frame, it)
            e.grid(i, 1)
            vars.append(e)

        self.start_end_btn = ItemButton(root, "Start", self.start)
        self.start_end_btn.grid(3, 2)
        self.pause_btn = ItemButton(root, "Pause", self.pause)
        self.pause_btn.grid(3, 3)

    def run(self):
        self.root.mainloop()

    def start(self):
        self.task_timer.start()

    def end(self):
        self.task_timer.stop()

    def pause(self):
        if not self.task_timer.state:
            self.task_timer.pause()
            self.pause_btn.tv.set("Resume")
        else:
            self.task_timer.resume()
            self.pause_btn.tv.set("Pause")


if __name__ == '__main__':
    ItemWindow().run()
