"""
Test the logic used to parse and output
LabVIEW-compliant "xml".

An easy way to get test files to scan is
to just load all of the tests cases already saved for
sysvars testing. 
"""

import util
import pytest
import sys
from itertools import zip_longest
import difflib
import cfg_compare
fromfn = cfg_compare.fromfn  # make sure the correct one is imported!

skip_exp_fail = {
    "sysvars.case_small_float"
}

infos = util.load_test_cases("sysvars")
files = []
ids   = []
for i in infos:
    if i.name in skip_exp_fail:
        continue
    files.append(i.cff); ids.append(i.name+".cff")
    files.append(i.off); ids.append(i.name+".off")
    files.append(i.nff); ids.append(i.name+".nff")
    files.append(i.expected); ids.append(i.name+".expected")

@pytest.mark.parametrize("ff", files, ids=ids)
def test_lv_parse(ff):
    exp = util.load_file(ff)
    LV = fromfn(ff)
    res = LV.toxml()
    util.file_compare(exp, res)