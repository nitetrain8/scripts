import util
import pytest
import sys
import lv_parse
from itertools import zip_longest
import difflib

infos = util.load_test_cases("calfactors")
ids = [i.name for i in infos]

# global stopped
# stopped = False
@pytest.mark.parametrize("info", infos, ids=ids)
def test_calfactors_basic(info):
    # if not stopped:
    #     import pdb; pdb.set_trace()
    #     global stopped
    #     stopped = True
    info.run_merge()
    exp = util.load_file(info.expected)
    res = util.load_file(info.result)
    compare(exp, res)
    info.cleanup()

def flatten(s):
    LV = lv_parse.flatten(lv_parse.lv_parse_string(s))
    rv = []
    for key, v in LV.items():
        rv.append("%s: %s %s %s"%(key, v.name, v.type, v.val))
    return "\n".join(rv)

def compare(exp, res):
    """ Compare LV files carefully, since
    LV floating point output is inconsistent.

    This function is kind of slow, but fuck
    labview for being shit. 

    This function is horrid and hacky. oh well. 
    """

    __tracebackhide__ = True

    def wtf(i, e, r):
        return "Line %d: '%s' != '%s' (WTF?)"%(i, e, r)

    def _ezip(*args):
        return enumerate(zip_longest(*args, fillvalue=""), 1)

    def _isval(l):
        return l.lower().startswith("<val>") and l.lower().endswith("</val>")

    if exp != res:
        rv = util.diff3(flatten(exp), flatten(res))
        
        # this code block is triggered if there were differences
        # detected by raw string compare, but between the parsed
        # string lists. 

        if len(rv) == 1 and rv[0].startswith("<Unknown"):

            # for everything below here, the only way I know of that
            # this could possibly happen is due to floating point 
            # string representation mismatch (ie '0.001' vs '1e-3')
            # so, we do a bunch of hacky shit and try to determine whether
            # the files are -actually- different, or if it was just a 
            # string compare failure. 

            # If the mismatch is actual value mismatch, 
            # populate a new list of messages to be 
            # listed as the failure message. Otherwise 
            # (aka representation mismatch only), 
            # print a message to be displayed somewhere in 
            # the list of pass/fail messages as pytest runs. 

            # the check is done by seeing if the line is bookended
            # by `val` xml tags ('<val>123.456</val>', etc) and
            # extracting the element text to convert to float. 

            # float value comparison does no rounding - for the
            # types of floats we're comparing, there should be
            # no imprecision errors between e.g. 0.001 and 1e-3. 

            expl = exp.splitlines()
            resl = res.splitlines()
            rv2 = []
            print()
            for i, (e, r) in _ezip(expl, resl):
                if e == "" or r == "":
                    rv.append("Missing line %d: '%s' != '%s'"%(i, e, r))
                elif e != r:
                    if _isval(e) and _isval(r):
                        ef = float(e[5:-6])
                        rf = float(r[5:-6])
                        if ef != rf:
                            rv2.append(wtf(i, e, r)) # should never happen
                        else:
                            print("Warning - float format mismatch: '%s' != '%s'"%(e[5:-6], r[5:-6]))
                    else:
                        rv2.append(wtf(i, e, r))  # should never happen

            if rv2:
                util.raise_assert(rv2)

        else:
            # standard failure
            util.raise_assert(rv)
    
    assert True
