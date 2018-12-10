import re
from officelib.xllib import xladdress, xlcom


_sform_re = re.compile(r"\=SERIES\((.*?)\,(.*?)\,(.*?)\,(.*?)\)")
_value_re = re.compile(r"\$(.*?)\$(\d*?)$")

def _split_address(a):
    m = _value_re.match(a)
    if not m:
        raise ValueError(a)
    return m.groups()
    
def _move_addr(addr, offset):
    c, r = _split_address(addr)
    r = int(r) + offset
    return ''.join(("$", c, "$", str(r)))
    
def _move_form(form, offset_up, offset_down):
    sheet, form = form.split("!")
    s, e = form.split(":")
    s = _move_addr(s, -offset_up)
    e = _move_addr(e, offset_down)
    form = "".join((sheet, "!", s, ":", e))
    return form
    
    
def _expand_formula(formula, offset_down, offset_up):
    m = _sform_re.match(formula)
    if not m:
        raise ValueError(formula)
    nform, xform, yform, num = m.groups()
    xform = _move_form(xform, offset_up, offset_down)
    yform = _move_form(yform, offset_up, offset_down)
    full_form = "=SERIES(%s,%s,%s,%s)" % (nform, xform, yform, num)
    return full_form


def expand_series(series, offset_down, offset_up=0):
    with xlcom.screen_lock(series.Application):
        old_formula = series.Formula
        full_form = _expand_formula(old_formula, offset_down, offset_up)
        series.Formula = full_form
   
def _true(s):
    return True   

def expand_chart_data(chart, down=1, up=0, allow_cb=_true):
    with xlcom.screen_lock(chart.Application):
        for series in chart.SeriesCollection():
            if allow_cb(series):
                expand_series(series, down, up) 
    
def expand_data(xl=None, down=1, up=0, allow_cb=_true):
    if xl is None:
        xl = xlcom.Excel()
    for co in xl.ActiveSheet.ChartObjects():
        expand_chart_data(co.Chart, down, up, allow_cb)