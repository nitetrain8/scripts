import requests,urllib,json, logging, dateutil, queue, threading, networkx as nx, asyncio, aiohttp, gc, datetime
from officelib.xllib import *
from pywintypes import com_error
from itertools import zip_longest
import collections
import time

_urljoin = urllib.parse.urljoin
_urlencode = urllib.parse.urlencode


# In[11]:


class ConverterError(Exception):
    pass

class _RedmineConverter():
    def __init__(self):
        self._converters = {}
        
    def Register(self, kls):
        self._converters[kls] = dict(kls._converter_table)
        return kls  # allow function use as decorator
        
    def Deserialize(self, jobj, kls):
        try:
            tbl = self._converters[kls]
        except KeyError:
            raise
        
        obj = kls()
        for key, val in jobj.items():
            conv = tbl.get(key)
            if conv:
                if conv in self._converters:
                    val = self.Deserialize(val, conv)
                else:
                    val = conv(val)
            else:
                pass
                # pass : use val as-is (string)
            setattr(obj, key, val)
            
        for key in tbl.keys():
            if key not in jobj:
                setattr(obj, key, None)
        return obj
            
RedmineConverter = _RedmineConverter()     


# In[12]:


@RedmineConverter.Register
class Resource():
    _converter_table = [
        ("name", str),
        ("id", int),
        ("value", str)
    ]
    def __str__(self):
        return f"<{self.__class__.__name__} {self.name}, id={self.id}, v={repr(self.value)}>"
    __repr__ = __str__
    
    
@RedmineConverter.Register
class User():
    _converter_table = [
        ("name", str),
        ("id", int)
    ]
    def __str__(self):
        return f"<{self.__class__.__name__} {self.name}, id={self.id}>"
    __repr__ = __str__
    

def Datetime(d):
    return dateutil.parser.parse(d)


def CustomFields(cf):
    fields = {}
    for f in cf:
        fields[f['name']] = RedmineConverter.Deserialize(f, Resource)
    return fields

def Parent(p):
    return p['id']

@RedmineConverter.Register
class Issue():
    
    _converter_table = [
        ("author", User),
        ("custom_fields", CustomFields),
        ("fixed_version", Resource),
        ("status", Resource),
        ("created_on", Datetime),
        ("updated_on", Datetime),
        ("id", int),
        ("project", Resource),
        ("priority", Resource),
        ("due_date", Datetime),
        ("tracker", Resource),
        ("parent", Parent),
        ("closed_on", Datetime),
        ("start_date", Datetime),
        ("assigned_to", User),
        ("estimated_hours", float)
    ]
    
    def __init__(self):
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}: '{self.subject}'>"


# In[13]:


class Client():
    def __init__(self, url, key):
        if not url.startswith("http"):
            url = "https://"+url
        self._url = url
        self._key = key
        self._sess = requests.Session()
        self._headers = {'X-Redmine-API-Key': self._key}
        self._Issues = None
        
    def _rawget(self, url, headers):
        r = self._sess.get(url, headers=headers)
        r.raise_for_status()
        return r
    
    def _prep(self, path, opts):
        base = _urljoin(self._url, path)
        qs = _urlencode(opts)
        url = f"{base}?{qs}"
        return url, self._headers
    
    def get(self, path, opts):
        url, headers = self._prep(path, opts)
        return self._rawget(url, headers)
    
    async def get_async(self, session, path, opts):
        url, headers = self._prep(path, opts)
        async with session.get(url, headers=headers) as r:
            r.raise_for_status()
            return await r.json()
        
    def superget(self, key, path, opts=None):
        base = _urljoin(self._url, path)
        opts = opts or {}
        pool = RedmineSuperPool(self._headers, key, base, opts)
        results = pool.wait()
        count = pool.total_count()
        assert len({x['id'] for x in results}) == count
        return results
            
    @property
    def Issues(self):
        if self._Issues is None:
            self._Issues = IssuesClient(self)
        return self._Issues
    
    def close(self):
        self._Issues = None
        
     
def _step_range(start, total_count, step):
        end = total_count - 1
        
        # extra is the amount needed to ensure
        # the final iteration includes the "end"
        # value
        extra = step - (end - start) % step 
        stop = end + extra
        return range(start, stop, step)

def _test_step_range():
    def test_step_range(start=None, limit=100, total_count=1021):
        if start is None:
            start = limit
        for i in _step_range(start, total_count, limit):
            pass
        ilast = total_count - 1
        assert (i + limit > ilast)
    
    for start in (0, None):
        for l in (99, 100, 101):
            for i in range(900, 1100):
                test_step_range(start, l, i)
_test_step_range()
    
    
class RedmineSuperPool:
    def __init__(self, headers, key, path, opts):
        self._headers = headers
        self._path = path
        self._opts = opts
        self._key = key
        
        self._thread = threading.Thread(None, target=self._run, daemon=True)
        self._stop = False
        self._results = []
        self._total_count = 0
        self._thread.start()
        
    def _run(self):
        self._stop = False
        main = self._main()
        asyncio.run(main)
        
    def wait(self):
        self._thread.join()
        return self._results
    
    def total_count(self):
        return self._total_count
        
    def _urlify(self, path, opts):
        return f"{path}?{_urlencode(opts)}"
        
    async def _main(self):
        loop = asyncio.get_running_loop()
        
        # don't choke the network :)
        concurrent_connection_limit = 100
        sem = asyncio.Semaphore(concurrent_connection_limit)
        
        async with aiohttp.ClientSession(headers=self._headers) as session:
            
            # first call gets total count. It is probably not possible
            # to avoid this unless the number of issues is known in advance.
            opts = self._opts
            opts['limit'] = limit = 100
            opts['offset'] = offset = 0
            url = self._urlify(self._path, opts)
            j = await self._fetch_result(session, url, sem)
            
            self._total_count = total_count = j['total_count']
            
            tasks = []
            for offset in _step_range(limit, total_count, limit):
                opts['offset'] = offset
                url = self._urlify(self._path, opts)
                task = loop.create_task(self._fetch_result(session, url, sem))
                tasks.append(task)
            await asyncio.gather(*tasks)
            assert len(self._results) == total_count, (len(self._results), total_count)
                
    async def _fetch_result(self, session, url, sem):
        async with sem:
            j = await self._fetch(session, url)
            self._results.extend(j[self._key])
            return j
            
    async def _fetch(self, session, url):
        ret = await session.get(url)
        ret.raise_for_status()
        return await ret.json()
        
    
class IssuesClient():
    def __init__(self, client):
        self._client = client
        
    def filter(self, /, **opts):
        raw = self._client.superget("issues", "/issues.json", opts)
        def parse(x):
            return RedmineConverter.Deserialize(x, Issue)
        return [parse(x) for x in raw]
    


# In[14]:


def resource_name(r):
    if r is not None:
        return r.name
    return ""


class Column2:
    def __init__(self, top):
        self._top = top
        self._first = top.GetOffset(1, 0)
        

class ColumnConfig2:
    def __init__(self, cells, top_left):
        self._top_left = top_left
        self._cells = cells
        self._lcol = []
        self._dcol = {}
        
    def add(self, name):
        offset = len(self._lcol)
        top = self._top_left.GetOffset(0, offset)
        col = Column2(top)
        self._lcol.append(col)
        self._dcol[name] = offset
        
    def rowify_data(self, data):
        # turns "header": <data>
        # key-value pairs into a row as a list
        # of values in the correct order
        row = [None] * len(self._lcol)
        for k, v in data.items():
            row[self._dcol[k]] = v
        return row
    
    def full_range(self, rows):
        tl = self._top_left
        br = tl.GetOffset(rows, len(self._lcol) - 1)
        return self._cells.Range(tl, br)
    
    def data_range(self, rows):
        """
        param rows: # of data rows
        """
        tl = self._top_left.GetOffset(1, 0) # top left data cell
        br = tl.GetOffset(rows - 1, len(self._lcol) - 1)
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
        y = []
        for i in range(n):
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
    
#     def _unionify2(self, ranges):
#         """ This should be the optimized version
#         of the above, but it is untested.
        
#         I believe in theory this method starts being
#         faster around a list size 29*29 or 30*29, so in 
#         practice it probably does not matter. 
#         """
#         ranges = list(ranges)
        
#         U = self.ws.Application.Union
#         def Union(chunk): return U(*chunk)
 
#         chunks = ranges
#         while len(chunks) > 30:
#             chunks = list(map(Union, _mygroup(chunks, 30)))
#         return Union(chunks)
            
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
        statuses.remove("Closed")
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
        
def _dfs_visit(g, parent, visit, depth):
    for node in sorted(g.successors(parent)):
        visit(node, depth)
        _dfs_visit(g, node, visit, depth + 1)
    
def dfs_visit(g, visit):
    roots = [n for n, idg in g.in_degree() if idg == 0]
    for r in sorted(roots):
        visit(r, 0)
        _dfs_visit(g, r, visit, 1)


# In[15]:


def Save(wb, *a,**k):
    wb.Application.DisplayAlerts = False
    try:
        wb.SaveAs(*a,**k)
    finally:
        wb.Application.DisplayAlerts = True
    
def sharepoint_path():
    return "https://pbsbiotech.sharepoint.com/sites/SoftwareEngineeringLV1/Shared Documents/Project Management/Software Active Development.xlsx"
    
def save_to_sharepoint(wb):
    fp = sharepoint_path()
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


# In[16]:


def make_graph():
    key = "7676add9cac6631410403671cdd7850311987898"
    client = Client("issue.pbsbiotech.com",key)
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
            visit(g, parent, node)
            _dfs_visit2(g, node, visit, depth + 1)
        
    def dfs_visit2(g, node, visit):
        visit(g, None, node)
        _dfs_visit2(g, node, visit, 1)
    
    def visit(g, parent, node):
        g.add_node(node)
        if parent is not None:
            g.add_edge(parent, node)
    
    # second graph - only what we care about
    # this routine loads all Active Development issues as well
    # as any children, regardless of milestone
    
    fv_active = 96  # sprint/milestone ID for software Active Development
    g2 = nx.DiGraph()
    for i in ad_issues:
        if i.fixed_version is None or i.fixed_version.id != fv_active:
            continue
        dfs_visit2(g, i.id, visit)

#     def show_tree(node, depth):
#         print(" "*depth + str(node))           
    # dfs_visit(g, show_tree)
    
    return g2, ad_map


# In[17]:


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
            raise RunTimeError("Failed to load win32com.client.constants dictionary")
        
        print("Workaround successful. Resuming activity...")
        
    return xl


# In[19]:


# issue fetch routine now uses superget(), which essentially eliminates the network bottleneck

# note: superget is slower than the old method if the filter_with_children method
# doesn't find many children, but significantly faster otherwise and is by far
# the most scalable and flexible method since it fetches the entire issue list.

# visitor design now defers pasting data until the full table is ready, and AGGRESSIVELY
# combines data ranges while formatting to minimize COM calls for maximum execution speed. 

# Note that for both Redmine and COM, the execution bottleneck is server<->client interop
# latency. Some procedures are done in a slightly inefficient way because client-side
# execution and filtering is effectively instant while interop sees a roughly fixed per-call
# delay. 

start = time.time()
print("Downloading issues and making graph...")
g, ad_map = make_graph()

template_path = os.path.expanduser("~\\documents\\pbs\\wip procedures-reports\\project task template2.xlsx")

print("Opening background Excel task...")

xl = background_excel()
with HiddenXl(xl):
    wb = xl.Workbooks.Open(template_path)
    ws = wb.Worksheets("Outline")

    print("Creating worksheet...")
    visitor = PlanInitVisitor(ws, g, ad_map)
    with screen_lock(xl):
        visitor.visit_all()
        visitor.finish()

    print("Saving to sharepoint...")
    #save_to_sw_eng(wb)
    try:
        save_to_sharepoint(wb)
    except com_error:
        print("Save failed :(")
    else:
        print("Success! Wrapping up...")
    
# increments major version
#if 0: publish(wb)


xl.ActiveWindow.WindowState = xlc.xlNormal

# release & clean up COM object references
del visitor, xl, wb, ws
gc.collect()
gc.collect()  # just in case :)


# In[ ]:




