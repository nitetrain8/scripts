import collections


from .table import BasicTable
from .xlhelpers import xlc
from .unionify import unionify_addresses
from .redmine.api import resource_attrib      

class TaskRecord:
    """ Record of a task. Turns an issue and outline # into a
    "database row" (excel table row).
    """
    def __init__(self, outline=None, id=None, subject=None, 
                assigned_to=None, done_ratio=None, status=None, 
                hours=None, priority=None, updated=None, due=None):
        
        self.outline = outline
        self.id = id
        self.subject = subject
        self.assigned_to = assigned_to
        self.done_ratio = done_ratio
        self.status = status
        self.hours = hours
        self.priority = priority
        self.updated = updated
        self.due = due

    @classmethod
    def from_issue(cls, outline, iss):
        return cls(outline, str(iss.id), iss.subject, resource_attrib(iss.assigned_to, "name"), 
        iss.done_ratio / 100, resource_attrib(iss.status, "name"), iss.estimated_hours or 0,
        resource_attrib(iss.priority, "name"), iss.updated_on, iss.due_date)
    
    def get_tuple(self):
        return (
            self.outline,
            self.id,
            self.subject,
            self.assigned_to,
            self.done_ratio,
            self.status,
            self.hours,
            self.priority,
            self.updated,
            self.due
        )
    as_tuple = get_tuple  # because I keep making that mistake
            

class ADTable:
    """
    Data model and business logic for a task table.

    Does not do direct interface with the excel worksheet,
    but does rely on win32com for values for constants. 
    """    
    _column_labels_ = [
        ("outline",         "#"           ),
        ("id",              "Issue"       ),
        ("subject",         "Name"        ),
        ("assigned_to",     "Assignee(s)" ),
        ("done_ratio",      "% Done"      ),
        ("status",          "Status"      ),
        ("estimated_hours", "Hours"       ),
        ("priority",        "Priority"    ),
        ("updated_on",      "Last Update" ),
        ("due_date",        "Due Date"    )
    ]
    def __init__(self):
        self.records = []
        self.row_count = 0

        # if we're deeper than this, something is very wrong
        # I think 5 should be the absolute max
        # maps indent (int) -> rows (list of row indexes)
        self.indent = [[] for _ in range(32)]

    def _simple_fill(self, rng, fill):
        # copied from vba macro
        interior = rng.Interior
        if fill == 'gray':
            interior.Pattern = xlc.xlSolid
            interior.PatternColorIndex = xlc.xlAutomatic
            interior.ThemeColor = xlc.xlThemeColorDark1
            interior.TintAndShade = -0.14996795556505
            interior.PatternTintAndShade = 0
        elif fill == "darkgray":
            interior.Pattern = xlc.xlSolid
            interior.PatternColorIndex = xlc.xlAutomatic
            interior.ThemeColor = xlc.xlThemeColorDark1
            interior.TintAndShade = -0.349986266670736
            interior.PatternTintAndShade = 0
        elif fill == 'none':
            interior.Pattern = xlc.xlNone
            interior.TintAndShade = 0
            interior.PatternTintAndShade = 0
        else:
            raise ValueError(fill)        

    def _borderify(self, rng):
        borders = [
            xlc.xlEdgeTop,
            xlc.xlEdgeLeft,
            xlc.xlEdgeRight,
            xlc.xlEdgeBottom,
            xlc.xlInsideVertical,
            xlc.xlInsideHorizontal
        ]
        for b in borders:
            bb = rng.Borders(b)
            bb.LineStyle = xlc.xlContinuous
            bb.ColorIndex = 0
            bb.TintAndShade = 0

    def _create_table(self, ws, origin):
        table = BasicTable(ws, origin, self._column_labels_)
        for record in self.records:
            row = record.as_tuple()
            table.add_row(row)
        return table
            
    def create(self, ws, origin):
        
        table = self._create_table(ws, origin)
        
        # Format the target number ranges before
        # pasting values, esp the row data.
        self._preformat_table(table)
        self._format_numbers(table)
        
        # paste
        table.apply_header()
        table.apply_data()
        
        # generic formatting
        self._format_header(table)
        self._center_columns(table)
        self._bold_columns(table)
        self._format_tasks(table)
        self._add_hyperlinks(table)
        self._add_cond_format_due(table)
        self._add_cond_format_updated(table)
        
        # autofit before adding filter boxes
        self._superfit(table)
        self._autofilter_status(table)
        

    def _add_hyperlinks(self, table):
        """Adds hyperlinks to the table using the issue id.

        Args:
            table (BasicTable): basic table.
        """        
        for i, record in enumerate(self.records):
            cell = table.cell_range("id", i)
            iid = record.id
            href = "https://issue.pbsbiotech.com/issues/" + iid
            table.ws.Hyperlinks.Add(Anchor=cell, Address=href, TextToDisplay=iid)
        
        # hyperlinks are underlined by default, but that looks ugly
        table.column_range("id").Font.Underline = False

    def _autofilter_status(self, table):
        filtered = ("Closed","Rejected")
        statuses = {record.status for record in self.records if record.status is not None}
        for s in filtered:
            statuses.discard(s)
        rng = table.table_range()
        field = table.column_index("status") + 1  # 1-based index
        rng.AutoFilter(Field=field, Criteria1=list(statuses), Operator=xlc.xlFilterValues)
    
    def _add_cond_format_due(self, table):
        """Sets due date column to highlight tasks if they are 
        due on or earlier than the current date. 
        
        This uses two rules:
        1. FormatCondition to ignore blank cells, and stop evaluating conditions if found
        2. FormatCondition to apply the date-based highlighting
        
        The combination is required to get the effect of:
        "highlight if (due date <= today) AND (cell is not blank)"
        
        The "blank" rule is executed first, and StopIfFound is set to true to prevent
        the date rule from firing on blank (non-date) cells.

        Args:
            table (BasicTable): basic table.
        """        
        due = table.column_range("due_date")
        
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

    def _add_cond_format_updated(self, table):
        updated = table.column_range("updated_on")
        cond = updated.FormatConditions.Add(Type=xlc.xlTimePeriod, DateOperator=xlc.xlLast7Days)
        cond.StopIfTrue = False
        
        # "Green Fill with Dark Green Text"
        font = cond.Font; interior = cond.Interior
        font.Color = -16752384
        font.TintAndShade = 0
        interior.PatternColorIndex = xlc.xlAutomatic
        interior.Color = 13561798
        interior.TintAndShade = 0

    def _format_header(self, table):
        hrange = table.header_range()
        hrange.Font.Bold = True
        self._simple_fill(hrange, "darkgray")
        self._borderify(hrange)

    def _preformat_table(self, table):
        data_range = table.data_range()
        data_range.HorizontalAlignment = xlc.xlLeft
        data_range.Font.Bold = False
        data_range.IndentLevel = 0
        data_range.Font.Size = 10
        self._simple_fill(data_range, 'none')

    def _center_columns(self, table):
        center = ("id", "done_ratio", "status", "estimated_hours", "priority", "updated_on", "due_date")
        for name in center:
            rng = table.entire_column_range(name)  # include header
            rng.HorizontalAlignment = xlc.xlCenter

        # center this one too. only Name should be un-centered. 
        rng = table.header_cell_range("assigned_to")
        rng.HorizontalAlignment = xlc.xlCenter

    def _bold_columns(self, table):
        # column bolding
        always_bold = ("outline",)
        for name in always_bold:
            rng = table.column_range(name)
            rng.Font.Bold = True
        
    def _superfit(self, table):
        for rng in table.iter_column_ranges():
            col = rng.EntireColumn
            col.ColumnWidth = 255
            col.AutoFit()

    def _format_tasks(self, table):

        boldgray = []
        indents = [[] for _ in range(len(self.indent))]

        # step 1 - build lists of ranges
        for lvl, rows in enumerate(self.indent):
            # bold/gray or indent. # side effect: indentsr[0] = None (step 2)
            if lvl == 0:
                row_ranges = (table.row_address(r) for r in rows)
                boldgray.extend(row_ranges)
            else:
                outline_ranges = (table.cell_address("outline", r) for r in rows)
                subj_ranges = (table.cell_address("subject", r) for r in rows)
                indents[lvl].extend(subj_ranges)
                indents[lvl].extend(outline_ranges)
        
        # step 2 - unify ranges, including all indent ranges
        boldgrayr = unionify_addresses(boldgray, table.cr, table.Union)
        indentsr = [unionify_addresses(ind, table.cr, table.Union) 
                        if ind else None for ind in indents]

        # step 3 - apply range formatting.
        # Only apply indent formatting to
        # indents where range is not None.
        boldgrayr.Font.Bold = True
        self._simple_fill(boldgrayr, "gray")
        for i, rng in enumerate(indentsr):
            if rng is None: continue
            rng.IndentLevel = i

    def _format_numbers(self, table):
        def _format(table, name, fmt):
            rng = table.column_range(name)
            rng.NumberFormat = fmt
        _format(table, "id", "@")
        _format(table, "outline", "@")
        _format(table, "done_ratio", "0%")
        _format(table, "estimated_hours", "0.0")
        _format(table, "due_date", "m/d/yyyy")
        _format(table, "updated_on", "m/d - h:mm AM/PM")
        
    def add_row(self, depth, outline, iss):
        record = TaskRecord.from_issue(outline, iss)
        self.records.append(record)
        self.indent[depth].append(self.row_count)
        self.row_count += 1


class OutlineNumber:
    def __init__(self):
        self.state = [0]
        
    def indent(self):
        self.state.append(0)
        
    def dedent(self):
        self.state.pop()
    
    def next(self):
        self.state[-1] += 1
        
    def get_str(self):
        return ".".join(map(str, self.state))
    
    def get_state(self):
        return self.state.copy()
    
    def increment(self):
        self.next()
        return self.get_state()


class MapTraverse:
    """ Can't find a better name for this class. """
    def __init__(self, map):
        self.outline = OutlineNumber()
        self.map = map
        
    def _dfs_search(self, g, node, visit):
        
        path = self.outline.increment()
        obj = self.map[node]
        visit(path, obj)  # no exception handling
        
        self.outline.indent()
        for child in sorted(g.successors(node)):
            self._dfs_search(g, child, visit)
        self.outline.dedent()
        
    def traverse(self, g, visit):
        roots = [node for node, i in g.in_degree() if i == 0]
        for node in sorted(roots):
            self._dfs_search(g, node, visit)


class TableCreator:
    def __init__(self, factory=ADTable):
        self.factory = factory
        
    def create(self, ws, g, idmap):
        s = MapTraverse(idmap)
        adtable = self.factory()
        
        # populates the AD table with records
        s.traverse(g, self.visit(adtable))
        adtable.create(ws, "A2")
        return adtable

    def visit(self, adtable):
        def _visit(path, obj):
            outline = ".".join(map(str,path))
            if len(path) == 1:
                outline += ".0"
            depth = len(path) - 1
            adtable.add_row(depth, outline, obj)
        return _visit