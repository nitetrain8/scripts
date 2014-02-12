"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

steps_report = "C:\\Users\\PBS Biotech\\Downloads\\weekendsteps.csv"
from officelib.pbslib.batchutil import ParseDateFormat
from scripts.test_stuff.tpidmany import full_open_batch, manyfile3
from datetime import datetime, timedelta


with open(steps_report, 'r') as f:
    f.readline()
    contents = [line.strip().split(',') for line in f.readlines()]

tests = []
data = iter(contents)

extracted = []


for _, datestring, step in data:
    fmt = ParseDateFormat(datestring)
    date = datetime.strptime(datestring, fmt)
    step = step.strip()
    extracted.append((date, step))

batch = full_open_batch(manyfile3)

r = 5
q_before = timedelta(minutes=60-r)
q_after = timedelta(minutes=60+r)


def in_range(steps, data, before=q_before, after=q_after):
    b = steps + q_before
    a = steps + q_after
    return b < data < a

param = iter(batch['TempModeActual'])
test_step = 'Set "TempModeUser" to Auto'

count = 0
wrong = []
for date, step in extracted:
    if step == test_step:
        count += 1
        try:
            start, pv = next((time, pv) for time, pv in param if time > date)
            next(param)
            data_time = next((time for time, v in param if v != pv))
        except StopIteration:
            print("foo")
            break
        if in_range(start, data_time):
            wrong.append((start, data_time))
        else:
            print(start)

print(count)
for a, b in wrong:
    print("start:", a, "end:", b)
print(len(wrong))
