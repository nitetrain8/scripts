import networkx as nx
import gc
import datetime
import os
import collections

from pywintypes import com_error # pylint: disable=no-name-in-module
from itertools import zip_longest
import time

from officelib.xllib import *
from .redmine import api
        

def resource_name(r):
    if r is not None:
        return r.name
    return ""

class ColumnConfig2:
    """ This class is still terrible but not as bad
    as it used to be. 

    It needs to just be a "Worksheet" wrapper designed
    to be specific to the Active Dev worksheet with 
    appropriate helper methods. 
    """
    def __init__(self, cells, top_left):
        self._top_left = top_left
        self._cells = cells
        self._dcol = {}
        
    def add(self, name):
        offset = len(self._dcol)
        if name in self._dcol:
            raise ValueError(f"Duplicate column: {name}")
        self._dcol[name] = offset
        
    def rowify_data(self, data):
        # turns "header": <data>
        # key-value pairs into a row as a list
        # of values in the correct order
        row = [None] * len(self._dcol)
        for k, v in data.items():
            row[self._dcol[k]] = v
        return row
    
    def full_range(self, rows):
        tl = self._top_left
        br = tl.GetOffset(rows, len(self._dcol) - 1)
        return self._cells.Range(tl, br)
    
    def data_range(self, rows):
        """
        param rows: # of data rows
        """
        tl = self._top_left.GetOffset(1, 0) # top left data cell
        br = tl.GetOffset(rows - 1, len(self._dcol) - 1)
        return self._cells.Range(tl, br)
        
    def col_data_range(self, name, rows):
        i = self._dcol[name]
        top = self._top_left.GetOffset(1, i)
        bot = top.GetOffset(rows - 1, 0)
        return self._cells.Range(top, bot)
    
    def cell_range(self, name, n):
        i = self._dcol[name]
        return self._top_left.GetOffset(n + 1, i)
    
    def data_from(self, row, *columns):
        return [row[self._dcol[i]] for i in columns]
    
    def data_from1(self, row, column):
        return row[self._dcol[column]]
    
    def row_range(self, n):
        left = self._top_left.GetOffset(n + 1, 0)
        right = left.GetOffset(0, len(self._dcol) - 1)
        return self._cells.Range(left, right)
    
    def xl_index(self, n):
        return self._dcol[n] + 1
    
    
def _mygrouper(iterable, n):
    """ yields chunks of up to n from iterable """
    it = iter(iterable)
    while True:
        # sloppy but easier than figuring out
        # the slicing math
        y = []
        for _ in range(n):
            try:
                o = next(it)
            except StopIteration:
                yield y
                return
            else:
                y.append(o)
        yield y
    
class PlanInitVisitor():
    def __init__(self, ws, g, issues):
        self.ws = ws
        self.g = g
        if not isinstance(issues, dict):
            issues = {i.id:i for i in issues}
        self.issues = issues
        self.cells = ws.Cells
        self.cr = self.cells.Range
        self.nseen = 0
        self.depth = 0
        self.stack = [0]
        self._data = []
        
        self.columns = ColumnConfig2(self.cells, self.cells.Range("A2"))
        
        spec = [
            "#",
            "Issue",
            "Name",
            "Assignee(s)",
            "% Done",
            "Status",
            "Hours",
            "Priority",
            "Last Update",
            "Due Date",
            "Weighted Score",
            "Deliverable ID",
            "Date1",
            "Notes/Current Action(s)",
        ]
        for s in spec:
            self.columns.add(s)
            
    def _indent(self):
        self.depth += 1
        self.stack.append(1)
        
    def _dedent(self, depth):
        diff = self.depth - depth
        self.depth = depth
        for _ in range(diff):
            self.stack.pop()
        self.stack[-1] += 1
        
    def _increment(self):
        self.stack[-1] += 1
        
    def _outline_number(self):
        if len(self.stack) == 1:
            return str(self.stack[0]) + ".0"
        return ".".join(map(str,self.stack))
    
    def _get(self, node):
        return self.issues[node]
    
    def _make_data(self, iss):
        data = {
            "#":                       self._outline_number(),
            "Issue":                   iss.id,
            "Name":                    iss.subject,
            "Assignee(s)":             resource_name(iss.assigned_to),
            "% Done":                  iss.done_ratio / 100,
            "Status":                  resource_name(iss.status),
            "Hours":                   iss.estimated_hours or 0,
            "Priority":                resource_name(iss.priority),
            "Weighted Score":          "",
            "Deliverable ID":          "",
            "Date1":                   "",
            "Notes/Current Action(s)": "",
            "Due Date":                iss.due_date,
            "Last Update":             iss.updated_on
         }
        return data
    
    def visit_all(self):
        dfs_visit(self.g, self.visit)
        
    def _handle_depth(self, depth):
        if depth > self.depth:
            self._indent()
        elif depth < self.depth:
            self._dedent(depth)
        else:
            self._increment()
            
    def _fill(self, cell, op):
        # copied from vba macro
        i = cell.Interior
        if op == 'gray':
            i.Pattern = xlc.xlSolid
            i.PatternColorIndex = xlc.xlAutomatic
            i.ThemeColor = xlc.xlThemeColorDark1
            i.TintAndShade = -0.14996795556505
            i.PatternTintAndShade = 0
        elif op == 'none':
            i.Pattern = xlc.xlNone
            i.TintAndShade = 0
            i.PatternTintAndShade = 0
        else:
            raise ValueError(op)
        
    def visit(self, node, depth):
        self._handle_depth(depth)
        iss = self._get(node)
        data = self._make_data(iss)
        row = self.columns.rowify_data(data)
        self._data.append(row)
        self.nseen += 1
    
    def _add_hyperlink(self, cell, iid):
        href = "https://issue.pbsbiotech.com/issues/" + iid
        self.ws.Hyperlinks.Add(Anchor=cell, Address=href, TextToDisplay=iid)
        
    def _apply_hyperlinks(self):
        for i, row in enumerate(self._data):
            iid = self.columns.data_from1(row, "Issue")
            cell = self.columns.cell_range("Issue", i)
            self._add_hyperlink(cell, str(iid))
        
        issue = self.columns.col_data_range("Issue", self.nseen)
        issue.Font.Underline = False
        
    def _disable_errors(self, rng):
        for cell in rng:
            try:
                cell.Errors.Item(xlc.xlNumberAsText).Ignore = True
            except com_error:
                # if there is no active error, the method throws an exception
                pass 
    
    def _format_indents(self):
        # format cells according to indent level
        
        gray = []
        bold = []
        indented = collections.defaultdict(list)
        for i, row in enumerate(self._data):
            outline_num = self.columns.data_from1(row, "#")
            indent = outline_num.count(".")
            
            if indent == 1 and outline_num.endswith(".0"):
                indent = 0
            
            name = self.columns.cell_range("Name", i)
            outline = self.columns.cell_range("#", i)
            
            if indent == 0:
                done = self.columns.cell_range("% Done", i)
                status = self.columns.cell_range("Status", i)
                bold.extend((name, done, status))
                gray.append(self.columns.row_range(i))
            
            indented[indent].extend((name, outline))
        
        if gray:       
            u = self._unionify(gray)
            self._fill(u, 'gray')
        
        if bold:
            bold.append(self.columns.col_data_range("#", self.nseen))
            u = self._unionify(bold)
            u.Font.Bold = True
        
        if indented:
            for lvl, cells in indented.items():
                u = self._unionify(cells)
                u.IndentLevel = lvl
    
    def _unionify(self, the_ranges):
        """ This neat little routine is used to combine a list
        of Range objects (e.g. cell or group of cells) into a 
        single Range object using Excel.Application.Union().
        
        This is used by other functions to apply bulk formatting
        operations with significantly reduced COM calls by 
        combining, for example, all cells in the Worksheet
        that need to have Font.Bold = True. 
        
        This can reduce the number of COM calls for a distinct
        formatting step by orders of magnitude.
        
        For whatever reason, the Union method takes up to 30
        arguments instead of taking a list, so a helper is used
        to pull chunks of 29 from the list at a time to combine
        with the existing union. This is slightly less optimal
        than recursively combining the list into groups of 30,
        but significantly easier to implement. 
        """
        
        ranges = list(the_ranges)
        assert ranges is not the_ranges  # shallow copy if the_ranges is list
        U = self.ws.Application.Union
        u = ranges.pop()  # simplifies algorithm. 
        for chunk in _mygrouper(ranges, 29):
            u = U(u, *chunk)
        return u
            
    def finish(self):
        
        data_target = self.columns.data_range(self.nseen)
        
        # reset target range formatting
        print("Applying formatting")
        data_target.Font.Bold = False
        data_target.IndentLevel = 0
        data_target.Font.Size = 10
        
        self._fill(data_target, 'none')
        self._format_indents()
        
        # unpacking.....
        
        def get(name): 
            return self.columns.col_data_range(name, self.nseen)
        
        outline = get("#")
        iid = get("Issue")
        name = get("Name")
        assignee = get("Assignee(s)")
        done = get("% Done")
        status = get("Status")
        hours = get("Hours")
        due = get("Due Date")
        priority = get("Priority")
        updated = get("Last Update")
        
        # set numbering formats
        iid.NumberFormat = "@"
        outline.NumberFormat = "@"
        done.NumberFormat = "0%"
        hours.NumberFormat = "0.0"
        due.NumberFormat = "m/d/yyyy"
        updated.NumberFormat = "m/d - h:mm AM/PM"
        
        U = self.ws.Application.Union
        
        # center these columns
        u = U(done, status, hours, iid, priority, updated)
        u.IndentLevel = 0
        u.HorizontalAlignment = xlc.xlCenter

        # paste data after applying basic formatting
        print("Pasting data...")
        data_target.Value2 = self._data
        
        # apply hyperlinks
        print("Adding fancy formatting...")
        self._apply_hyperlinks()
        
        # disable "number as text" error
        for c in (outline, iid):
            self._disable_errors(c)
            
        # force all cells to not wrap...
        for c in (outline, iid, name, assignee, done, status, hours, due,
                 updated, priority):
            self._force_nowrap(c.EntireColumn)
        
        self._conditional_format_updated_recent(updated)
        self._conditional_format_due_now(due)
          
        # Autofilter
        r = self.columns.full_range(self.nseen)
        field = self.columns.xl_index("Status")
        
        # allowed statuses
        statuses = {self.columns.data_from1(row, "Status") for row in self._data}
        statuses.discard("Closed")
        statuses = list(statuses)
        
        r.AutoFilter(Field=field, Criteria1=statuses, Operator=xlc.xlFilterValues)
        
    def _conditional_format_updated_recent(self, updated):
        # based on macro recorded
        # Conditional Formatting -> Highlight Cells Rules -> A Date Occurring -> Last 7 days
        cond = updated.FormatConditions.Add(Type=xlc.xlTimePeriod, DateOperator=xlc.xlLast7Days)
        cond.StopIfTrue = False
        
        # "Green Fill with Dark Green Text"
        font = cond.Font; interior = cond.Interior
        font.Color = -16752384
        font.TintAndShade = 0
        interior.PatternColorIndex = xlc.xlAutomatic
        interior.Color = 13561798
        interior.TintAndShade = 0
        
    def _conditional_format_due_now(self, due):
        """
        Sets due date column to highlight tasks if they are 
        due on or earlier than the current date. 
        
        This uses two rules:
        1. FormatCondition to ignore blank cells, and stop evaluating conditions if found
        2. FormatCondition to apply the date-based highlighting
        
        The combination is required to get the effect of:
        "highlight if (due date <= today) AND (cell is not blank)"
        
        The "blank" rule is executed first, and StopIfFound is set to true to prevent
        the date rule from firing on blank (non-date) cells.
        """
        
        # date rule
        date_cond = due.FormatConditions.Add(Type=xlc.xlCellValue, Operator=xlc.xlLessEqual, Formula1="=TODAY()")
        date_cond.StopIfTrue = False
        date_cond.SetFirstPriority()  # don't worry, see blank_cond
        font = date_cond.Font; interior = date_cond.Interior
        
        font.Color = -16383844
        font.TintAndShade = 0
        
        interior.PatternColorIndex = xlc.xlAutomatic
        interior.Color = 13551615
        interior.TintAndShade = 0
        
        # blank rule
        # Column letter is required for the "blank" formula:
        # this is the formula recorded by macro, unknown if a relative
        # or similar reference can be obtained in a less hacky way
        
        addr1 = due.Cells(1,1).GetAddress(False, False)
        blank_cond = due.FormatConditions.Add(Type=xlc.xlExpression, Formula1=f"=LEN(TRIM({addr1}))=0")
        blank_cond.SetFirstPriority()  # :)
        blank_cond.StopIfTrue = True
        
        # no format set
            
    def _force_nowrap(self, col):
        # grow to max column width, then autofit back to min for single row
        col.ColumnWidth = 255
        col.AutoFit()

#     def _unionify2(self, ranges):
#         """ This should be the optimized version
#         of the unionify method, but it is untested.
        
#         I believe in theory this method starts being
#         faster around a list size of 29*29 or 30*29, so in 
#         practice it probably does not matter. 
#         """
#         ranges = list(ranges)
        
#         U = self.ws.Application.Union
#         def Union(chunk): return U(*chunk)
 
#         chunks = ranges
#         while len(chunks) > 30:
#             chunks = list(map(Union, _mygroup(chunks, 30)))
#         return Union(chunks)
        
def _dfs_visit(g, parent, visit, depth):
    for node in sorted(g.successors(parent)):
        visit(node, depth)
        _dfs_visit(g, node, visit, depth + 1)
    
def dfs_visit(g, visit):
    roots = [n for n, idg in g.in_degree() if idg == 0]
    for r in sorted(roots):
        visit(r, 0)
        _dfs_visit(g, r, visit, 1)


def Save(wb, *a,**k):
    wb.Application.DisplayAlerts = False
    try:
        wb.SaveAs(*a,**k)
    finally:
        wb.Application.DisplayAlerts = True
    
def save_to_sharepoint(wb, fp):
    Save(wb, fp, CreateBackup=False, AddToMru=True)
    
def checkout(wb):
    # The check in/out process is REALLY
    # kludgy from VBA. Check out essentially never
    # works without waiting a short period of time
    # for ... something ... to connect.
    
    # Regardless, we can reliably
    # perform checkout by looping until it works.
    
    # 5 second timeout to be safe. 
    
    xl = wb.Application
    end = time.time() + 5  # 5 second timeout
    while True:
        try:
            xl.Workbooks.CheckOut(wb.FullName)
        except Exception:
            if time.time() > end:
                raise
            time.sleep(0.2)  # give it a chance to think
        else:
            return
    
def publish(wb):
    checkout(wb)
    wb.CheckInWithVersion(True, "", True, xlc.xlCheckInMajorVersion)

def make_graph(key):
    client = api.Client("issue.pbsbiotech.com",key)
    ad_issues = client.Issues.filter(status_id="*")
    ad_map = {i.id:i for i in ad_issues}

    # first graph - all issues
    g = nx.DiGraph()
    for i in ad_issues:
        iid = i.id
        g.add_node(iid)
        pid = i.parent
        if pid is not None:
            g.add_edge(pid, iid)

    if not nx.is_forest(g):  # should not be possible
        raise ValueError("Circles in graph :(") 
    
    # simple DFS impl for (parent, node) pair callbacks
    def _dfs_visit2(g, parent, visit, depth):
        for node in sorted(g.successors(parent)):
            visit(parent, node)
            _dfs_visit2(g, node, visit, depth + 1)
        
    def dfs_visit2(g, node, visit):
        visit(None, node)
        _dfs_visit2(g, node, visit, 1)
    
    # second graph - only what we care about
    # this routine loads all Active Development issues as well
    # as any children, regardless of milestone
    
    fv_active = 96  # sprint/milestone ID for software Active Development
    
    g2 = nx.DiGraph()
    def visit(parent, node):
        g2.add_node(node)
        if parent is not None:
            g2.add_edge(parent, node)
    
    for i in ad_issues:
        if i.fixed_version is None or i.fixed_version.id != fv_active:
            continue
        dfs_visit2(g, i.id, visit)

    return g2, ad_map

def _check_constants():
    try:
        xlc.xlNormal
        xlc.xlSolid
        xlc.xlAutomatic
        xlc.xlNone
    except AttributeError:
        return False
    return True

def _get_xl_app():
    return win32com.client.DispatchEx("Excel.Application")

def background_excel():

    # It is possible (seems to happen after system updates) for
    # the win32com.client.constants dictionary to fail to populate,
    # due to some cache (perhaps the AppData/local/Temp folder?)
    # being cleared. 

    # Because the DispatchEx method is fully dynamic,
    # the constants dict isn't populated and all constant values must be
    # known from other sources. By default, the xlc constants
    # object uses win32com.client.constants, populated when
    # gencache.EnsureDispatch is used. 

    # test a few of the constants here - if they work, go ahead. Otherwise,
    # use the gencache method to try to force win32com to build the dicts.
    # This method has drawbacks so issue a warning to user. 
    
    # Test Protocol:
    # 1. Delete ~/AppData/Local/Temp/gen_py/<python version>
    # 2. Comment-out any code saving the workbook to sharepoint (or other)
    # 3. Restart the notebook & run all cells
    # 4. Verify it all works
    # 5. Close excel & verify no lingering excel processes
    # 
    # Run with and without a separate workbook opened by user 
    
    # Tested 6/3/2020 - seems to work just fine
    
    xl = _get_xl_app()
    if not _check_constants():
        print("Warning: Excel constants dictionary not initialized. Attempting workaround...")
        
        # Attempt to populate the dicts using gencache
        xl2 = win32com.client.gencache.EnsureDispatch("Excel.Application")
        
        # We don't want the Excel process to linger, but we also want to
        # try to avoid nuking a user's excel process if they're using it already.
        if xl2.Workbooks.Count == 0:
            xl2.Quit()
        
        del xl2
        gc.collect()
        
        # try again, bail if fail
        if not _check_constants():
            raise RuntimeError("Failed to load win32com.client.constants dictionary") 
        
        print("Workaround successful. Resuming activity...")
        
    return xl