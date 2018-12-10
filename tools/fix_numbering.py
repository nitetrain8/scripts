from pywintypes import com_error
from officelib.xllib import xlcom

_g_xl = None

def _get_selection(s=None):
    global _g_xl
    if s is not None:
        return s.Application, s
    if _g_xl is None:
        _g_xl = xlcom.Excel()
    return _g_xl, _g_xl.Selection

def fix_proj_outline(s=None, start=1):
    if s is None:
        xl,s=_get_selection()
    else:
        xl = s.Application
    level = start - 1
    state = [level, 0]
    with xlcom.screen_lock(xl):
        for c in s:
            if c.EntireRow.Hidden:
                continue
            il = c.IndentLevel
            if il > level:
                if il >= len(state):
                    state.append(1)
                state[il] = 1
            else:
                state[il] += 1
            value = ".".join("%d" % n for n in state[:il+1])
            c.Value = value
            level = il

def fix_ppd_outline(s, tmplt, n=1):
    # Need to populate a list here... iteration
    # Seems to not work for some reason
    pgs = [p for p in s.Paragraphs]
    
    for p in pgs:
        t = tmplt % n
        n += 1
        p.Range.Text = t
    
def next_cell(cell):
    r = 2
    cma = cell.MergeArea.Address
    while True:
        c = cell.Offset(r, 1)
        r += 1
        try:
            ma = c.MergeArea.Address
        except com_error:
            return c
        if ma != cma:
            return c
    
def fix_proc_steps(cell, v=1, end_cb=None):
    state=[v-1]

    if cell.Rows.Count > 1:
        # multirow cell or multiple rows selected
        if cell.Offset(1,1).MergeArea.Address != cell.Offset(cell.Rows.Count).MergeArea.Address:
            raise ValueError("Highlight single row for this function, not multiple!")
    if cell.Columns.Count > 1:
        sc = cell.Columns.Count
        cc = cell.Offset(1,1).MergeArea.Columns.Count
        if sc != cc:
            raise ValueError("Don't know how to handle non-merged cells in single row")
    
    cell = cell.Offset(1,1)
    
    while True:
        
        if cell.IndentLevel > len(state)-1:
            state.append(0)
        elif cell.IndentLevel < len(state)-1:
            del state[-1]
        state[-1] += 1
        
        cv = cell.Value
        if end_cb is None:
            if not cv:
                break
        else:
            if end_cb(cell, cv, state):
                break

        try:
            n, ct = cv.split(" ", 1)
            int(n[0])
        except (ValueError, AttributeError):
            # empty cell, or wasn't a numeric step; skip
            cell = next_cell(cell); continue

        nn = ".".join(str(i) for i in state)
        nv = " ".join((nn+".", ct))
        cell.Value = nv
        cell = next_cell(cell)
        