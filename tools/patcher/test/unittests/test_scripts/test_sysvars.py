import util
import pytest
import sys
import lv_parse
from itertools import zip_longest
import difflib

infos = util.load_test_cases("sysvars")
ids = [i.name for i in infos]

@pytest.mark.parametrize("info", infos, ids=ids)
def test_sv_merge_basic(info):
    info.run_merge()
    exp = util.load_file(info.expected)
    res = util.load_file(info.result)
    util.file_compare(exp, res, sv_flattenify)
    info.cleanup()

def sv_flattenify(s):
    lv = lv_parse.lv_parse_string(s)
    rv = ['\n']
    for g in lv:
        for v in g:
            rv.append("%s.%s: %s (type %s)"%(g.name, v.name, v.val, v.type))
    return "\n".join(rv)


































#############################
# Old comparison code - ignore
#############################
def simplediff(exp,res):
    e = sv_flattenify(exp)
    r = sv_flattenify(res)
    d = util.diff(e,r)
    if not d:
        return util.diff(exp, res)
    return d

def sv_superdiff1(exp, res):
    """ Parse into LVType objects and manual compare.... """

    # XXX in hindsight this is overkill
    # just diff the lines. 
    res = []
    lve = lv_parse.lv_parse_string(exp)
    lvr = lv_parse.lv_parse_string(res)

    def missing(e,r):
        n1 = e.name if e else ""
        n2 = r.name if r else ""
        res.append("Extra / missing item: %s != %s" % (n1, n2))

    def check(e,r,attr,m=""):
        m = m or attr.capitalize()
        a = getattr(e,attr)
        b = getattr(r, attr)
        if a != b:
            res.append("%s Mismatch: '%s' != '%s'"%(m,a,b))

    def checktype1(e,r):
        check(e,r,'name')
        check(e,r,'type')

    def checktype2(e,r):
        checktype1(e,r)
        check(e,r,'val')

    for ge, gr in zip_longest(lve, lvr, fillvalue=None):
        if ge is None or gr is None:
            missing(ge, gr)
        else:
            checktype1(ge, gr)
            for ve, vr in zip_longest(ge, gr):
                if ve is None or vr is None:
                    missing(ge, gr)
                else:
                    checktype2(ve, vr)
    return "\n".join(res)

def sv_simplediff(exp, res):


    # check for simple, common things that might be
    # errors in the test setup before defaulting to 
    # the more intensive error checking.
    # The intent here is to simplify the process of 
    # determining where the source of the error came
    # from. 

    # whitespace mismatch:
    e = exp.strip()
    r = res.strip()
    if e == r:
        return "Trailing whitespace in file"
    el = e.splitlines()
    rl  = r.splitlines()

    # an extra line somewhere is probaby a whoops
    # abort on first mismatched line
    if len(el) != len(rl):

        # check for random blank lines
        def cblank(l):
            blanklines = 0
            for s in l:
                if not s.strip():
                    blanklines += 1
            return blanklines

        a = cblank(el)
        b = cblank(rl)
        if a > 2 or b > 2:
            return "Random blank lines in files"

    return util.diff(el, rl)

def sv_superdiff(el, rl):
    badlines = []
    for i, (es, rs) in enumerate(zip_longest(el, rl, fillvalue=None), 1):
        if es != rs:
            if es.strip() == rs.strip():
                badlines.append("Line %d: Trailing whitespace"%i)
            else:
                badlines.append("Line %d: '%s' != '%s'"%(i, es, rs))
    return "\n".join(badlines)
