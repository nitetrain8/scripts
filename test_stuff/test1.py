"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'
mylist = [
"_settings",

"_temp_times",
"_temp_pvs",

"_heat_times",
"_heat_pvs",

"_top_left_address",
"_top_left_coords",
"_linear_start_cell",
"_linear_end_cell",
        ]
import re

magic_re = r"[_](\w)"
mynewlist = []
for i in mylist:
    spots = i.split('_')
    for i, s in enumerate(spots):
        try:
            spots[i] = s[0].upper() + s[1:]
        except:
            pass
    mynewlist.append(''.join(spots))

print(mynewlist)
