
import itertools

def run():
    sps = itertools.cycle((0.02, 0.04, 0.06, 0.08, 0.1))
    while True:
        sp = next(sps)
        try:
            app.setmg(1, sp)
        except Exception:
            try:
                app.login()
                app.setmg(1, sp)
            except Exception:
                app.reconnect()
                app.login()
                app.setmg(1, sp)

        except KeyboardInterrupt:
            return

        txt = input("Main Gas: %d mLPM" % int(1000*sp))

from officelib.xllib import xlcom
from officelib import const
from officelib.xllib.xladdress import cellStr

def extract_ws_data(ws):
    ws_data = []
    for n in (2, 3, 4):
        name = "MFC #%d" % n
        mfc_data = (name, extract_ws_mfc_data(ws, name))
        ws_data.append(mfc_data)
    return ws_data
    
def extract_ws_mfc_data(ws, name):
    cells = ws.Cells
    top_left = cells.Find(What=name, After=cells(1, 1), SearchOrder=const.xlByColumns)
    tl_c = top_left.Column
    tl_r = top_left.Row
    right = top_left.End(const.xlToRight).Column + 1
    bottom = tl_r + 4
    
    data = []
    for plus_row in range(bottom):
        row_data = []
        for col in range(tl_c, right):
            formula = "=%s" % cellStr(tl_r + plus_row, col)
            row_data.append(formula)
        data.append(row_data)
    return data

def extract_data():
    xl, wb = xlcom.xlBook2("M3-TR-3-004a.xlsx")
    rv = []
    for n in (0, 1, 2):
        name = "C-20 %d" % n
        ws = wb.Worksheets(name)
        data = extract_ws_data(ws)
        rv.append((name, data))
    return rv
    
def move_data():
    data = extract_data()
    xl, wb = xlcom.xlBook2("M3-TR-3-004a.xlsx")
    for name, ws_data in data:
        move_ws_data(wb, name, data)
        
def move_ws_data(wb, name, data):
    ws = wb.Worksheets(name)
    lpm_data = []
    for lpm in (0.02, 0.04, 0.06, 0.08, 0.10):
        lpm_data.append("%d mLPM" % (1000 * lpm)
        l_data = get_lpm_data(ws, data, lpm)
        
        for i, row in enumerate(l_data):
            
            if i != 0:
                l_data[i].append(None)
                lpm_data.(l_data)