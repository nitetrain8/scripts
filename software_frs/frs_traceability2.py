from officelib.xllib import *
from officelib.xllib import screen_lock as xl_screen_lock
from officelib.wordlib import *
from officelib.wordlib import screen_lock as wd_screen_lock
from officelib.const import xlconst as xlc, wdconst as wdc
from pywintypes import com_error
from scripts.tools.issuetracker import IssuetrackerAPI
from os.path import join as pjoin
import os
import re


def frs_nums(s):
    pos = s.find("FRS")
    num = s[pos+3:]
    return num.split(".")

def num_tuple(s):
    return tuple(int(i) for i in frs_nums(s))
    
def sort_key(t):
    return num_tuple(t[0])

def sort_frs_item(s):
    return num_tuple(s[0])


def paste_data(ws, data):
    cells = ws.Cells
    cr = cells.Range
    
    di = data[0].index("Tested") + 1
    
    header_start = cr("A1")
    
    frs_start = cr("A2")
    frs_end = header_start.Offset(len(data), 1)

    id_start = frs_start.Offset(1, 3)
    id_end = frs_end.Offset(1, 3)

    tested_start = id_start.Offset(1,2)
    tested_end = id_end.Offset(1,2)

    paste_start = header_start
    paste_end = frs_end.Offset(1, len(data[0]))
    
    holdup_end = tested_end.Offset(1, data[0].index("Is Holdup?")+1)
    
    with xl_screen_lock(ws.Application):
        paste_range = cr(paste_start, paste_end)
        print("Pasting test data")
        paste_range.Clear()
        paste_range.Value = data

        print("Applying alignment formatting")
        cr(frs_start, id_end).VerticalAlignment = xlc.xlTop
        cr(id_start, id_end).HorizontalAlignment = xlc.xlRight
        cr(tested_start, holdup_end).HorizontalAlignment = xlc.xlRight
        cr(tested_start, holdup_end).VerticalAlignment = xlc.xlTop

        print("Marking untested cells")

        cond = paste_range.FormatConditions.Add(Type=xlc.xlExpression, Formula1="=$C2<>\"y\"")
        rint = cond.Interior
        rint.PatternColorIndex = xlc.xlAutomatic
        rint.ThemeColor = xlc.xlThemeColorAccent2
        rint.TintAndShade = 0.399975585192419

        # col_os = paste_end.Column - paste_start.Column + 1
        # data_iter = iter(data); next(data_iter)
        # for offset, (item, level, t_id, tested, *__) in enumerate(data_iter, 1):
        #     row = cr(frs_start.Offset(offset, 1), frs_start.Offset(offset, col_os))
        #     if not tested:
        #         format_row(row)
        #     elif tested[0] == "=":
        #         if row[di].Value not in ("Y", "n/a"):
        #             format_row(row)
            
        #     row[1].IndentLevel = level + 1

        #print("Applying autofilter on untested items")
        #cr(paste_start.Offset(0, 1), paste_end).AutoFilter(Field=col_os, Criteria1="=")

        print("Applying column autofit")
        # fit after filter to account for width of filter icon
        for c in paste_range.Columns:
            c.EntireColumn.AutoFit()
            
        print("Applying row autofit")
        for r in paste_range.Columns:
            r.EntireRow.AutoFit()


def format_row(row):
    rint = row.Interior
    rint.Pattern = xlc.xlSolid
    rint.PatternColorIndex = xlc.xlAutomatic
    rint.ThemeColor = xlc.xlThemeColorAccent2
    rint.TintAndShade = 0.399975585192419
    rint.PatternTintAndShade = 0

    
def get_matrix_sheet(xl):
    wb = xl.Workbooks.Add()
    return wb.Worksheets(1)


_frs_match = re.compile(r"(.*FRS\d+)\.?([\d\.]*)").match
_toplevel_match = re.compile(r"^\>?[\+\*]{2}(FRS\d+)[\+\*]{2}(.*)$").match
_subitem_match = re.compile(r"^\>?[\+\*]+\s\*(FRS[\d\.]+)\:?\*\:?(.*)$").match
_item_match = re.compile(r"^\>?[\*]*\s*[\+\*]+(FRS[\d\.]+)\:?[\+\*]*\:?\s*(.*)$").match
_canceled_match = re.compile(r"^\>?[\*]*\s*-[\+\*]+(FRS[\d\.]+)\:?[\+\*]*\:?\s*(.*)-$").match
_header_match = re.compile(r"^\>?[\+\*]{2}([\d\.\w]+)[\+\*]{2}").match


def _key_match(k):
    m = _frs_match(k)
    if m:
        return m.groups()
    return k, ""


# Misc flags for FRS item status



def dump(node, level=0):
    for k, v in sorted(node.children.items()):
        print("."*level + str(v.id)+ " "+str(v._tests))
        dump(v, level+1)
        

class Node():

    OBSOLETE = 1<<0  # 1

    def __init__(self, nid, parent, flags=0):
        self.id = nid
        self.parent = parent
        self.children = {}
        self._tests = []
        self.text = ""
        self.milestone = ""
        self.priority = ""
        self.refs = set()
        self.flags = flags
        
    def is_obsolete(self):
        return self.get_flag(self.OBSOLETE)

    def set_flag(self, flag):
        self.flags |= flag

    def get_flag(self, flag):
        return self.flags & flag
        
    def add_test(self, id_test):
        self._tests.append(id_test)
        for c in self.children.values():
            c.add_test(id_test)
        
    def get_tests(self):
        return sorted(self._tests, key=str)
        
    def get(self, id_):
        return self.children.get(id_, None)
        
    def add_child(self, id_, flags=0):
        child = self.mk_child(id_, flags)
        self.children[id_] = child
        for t in self._tests:
            child.add_test(t)
        return child

    def remove_child(self, id_):
        child = self.children.get(id_)
        if child is not None:
            del self.children[id_]
            child.parent = None
    
    def mk_child(self, id_, flags=0):
        return self.__class__("%s.%s"%(self.id, id_), self, flags)
    
    def iter(self):
        # use .items() to sort by item order
        for _, v in sorted(self.children.items()):
            yield v
            yield from v.iter()

    def iter2(self, sort_func):
        children = sorted(self.children.values(), key=sort_func)
        for c in children:
            yield c
            yield from c.iter2(sort_func)
            
    def total_len(self):
        n = len(self.children)
        for v in self.children.values():
            n += v.total_len()
        return n
            
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.id)
    
    def is_tested(self, recurse=True):
        if self._tests:
            return True
        elif not self.children:
            return False
        elif recurse:
            for c in self.children.values():
                if not (c.is_tested() or c.is_na()):
                    return False
            return True
        return False
        
    def is_leaf(self):
        return not self.children
    
    def has_children(self):
        return bool(self.children)
        

class Root(Node):
    def __init__(self, key_func):
        super().__init__("", 0, None)
        self._key_func = key_func
        
    def mk_child(self, id_, flags):
        return Node(id_, self, flags)
        
    def add(self, key, flags):
        root_key, nums = self._key_func(key)
        child = self.get(root_key)

        # 2/25/19: this was done in a dumb way
        # basically, this block says "if there's
        # no root, and we're adding a child to the root,
        # create the root without the flags. Otherwise,
        # we're adding the root, so add the flags". 
        # This would be much easier if it used a split
        # type / num / tag system the way Reference object
        # works. c
        if not child:
            if nums:
                child = self.add_child(root_key)
            else:
                child = self.add_child(root_key, flags)
        if not nums:
            return child
        path = [int(i) for i in nums.split(".")]
        node = child
        
        for id_ in path:
            child = node.get(id_)
            if child is None:
                child = node.add_child(id_)
            node = child
        node.set_flag(flags)
        return node
    
    def lookup(self, key):
        root_key, nums = self._key_func(key)
        node = self.get(root_key)
        if not node or not nums:
            return node
        path = [int(i) for i in nums.split(".")]
        for id in path:
            node = node.get(id)
            if node is None: 
                return None
        return node


KNOWN_WEBFRS_MAX = 121


class BadFRSNumber(Exception):
    pass


def load_user_test_map(ws):
    cells = ws.Cells
    cr = cells.Range
    id_start = cells.Find("ID_TEST").Offset(2, 1)
    id_end = id_start.End(xlc.xlDown)
    frs_start = cells.Find("List Web FRS").Offset(2, 1)
    frs_end = frs_start.Offset(id_end.Row - id_start.Row + 1, 1)
    test_data = cr(id_start, frs_end).Value
    test_map = []
    fixed_frs = []
    
    # since we iterate over test data here, take the opportunity to
    # convert "\n" -> "\r\n".
    for row in test_data:
        id_test, frs = row[0], row[-1]
        iid_test = int(id_test)
        if id_test == iid_test:
            id_test = iid_test
        frs = str(frs or "")
        frs = [f.strip() for f in frs.splitlines()]
        fixed_frs.append(("\r\n".join(frs),))
        for f in filter(None, frs):
            test_map.append((f, id_test))
    webfrs_r = cr(frs_start, frs_end)
    webfrs_r.Value = fixed_frs
        
    test_map.sort(key=sort_key)
    return test_map


def build_frs_tree(all_items):
    root = Root(_key_match)
    for frs, flags, text in all_items:
        try:
            node = root.add(frs, flags)
        except:
            print(frs, flags, text)
            raise
        node.text = text
    return root

class Node2():
    def __init__(self, text, parent, flags):
        self.text = text
        self.parent = parent
        self.flags = flags
        self.children = []
    def add_child(self, c):
        self.children.add(c)

def build_fres_tree2(all_items):
    nodes = {}
    root = Node2("Root", None, 0)
    for frs, flags, text in all_items:
        path = frs[3:].split(".")
        if len(path) == 1:
            parent = root
        else:
            path.pop()
            parent = "FRS" + ".".join(path)
        nodes[frs] = Node2(text, parent, flags)

    nodes[root] = root
    for key, node in nodes.items():
        parent = nodes[node.parent]
        parent.add_child(node)
    return root


def _bad_frs_num(frs):
    if frs[:3] == "FDS":  # Old comments left in LV code by Cyth
        return
    #raise BadFRSNumber(frs)


def root_add_test_map(root, test_map):
    """
    :param test_map: list[(frs, id_test)]
    """
    for frs, id_test in test_map:
        node = root.lookup(frs)
        if not node:
            _bad_frs_num(frs)
        else:
            node.add_test(id_test)


# def _extract_frs_line(line):
#     matches = (
#         (_toplevel_match, 0),
#         (_subitem_match, 0),
#         (_canceled_match, FRS_NA),
#     )
#     for match, flags in matches:
#         m = match(line)
#         if m:
#             return m.group(1), flags, m.group(2)
#     return None, 0, ""
    

# def load_frs_from_issuetracker():
#     relevant = download_relevant_issues()
#     all_frs = {(None, 0, "")}
#     for v in relevant:
#         lines = v.description.splitlines()
#         for line in lines:
#             frs = _extract_frs_line(line)
#             all_frs.add(frs)
#     for i in range(1, KNOWN_WEBFRS_MAX + 1):
#         all_frs.add(("3.0WebFRS%03d" % i, 0, ""))
#     all_frs.remove((None, 0, ""))
#     return all_frs

def _extract_frs_lines(lines):
    start_matches = (
        (_item_match, 0),
        (_canceled_match, 1),
    )
    end_matches = (
        _item_match,
        _canceled_match,
    )
    i = 0
    while True:
        try:
            line = lines[i]
        except IndexError:
            break
        i += 1
        for match, flags in start_matches:
            done = False
            if not line:
                m = None
            else:
                m = match(line)
            if m:
                f = m.group(1)
                t = m.group(2).strip()
                l = [t]
                while True:
                    try:
                        line = lines[i].strip()
                    except IndexError:
                        done = True
                        break
                    if not line:
                        done = True
                        break
                    if any(m(line) for m in end_matches):
                        done = True
                        break
                    l.append(" " + line.strip())
                    i += 1
                text = "\n".join(l)
                yield f, flags, text
            if done:
                break  
    
# def _extract_frs_lines(lines):
#     start_matches = (
#         (_toplevel_match, 0, True),
#         (_subitem_match, 0, True),
#         (_canceled_match, FRS_NA, True),
#         (_header_match, 0, False)
#     )
#     current = []
#     f = None
#     c_flags = 0
#     parsing = False
#     for line in lines:
#         for matcher, flags, p in start_matches:
#             m = matcher(line)
#             if not m: 
#                 continue
#             parsing = p
#             if not parsing: 
#                 break
#             yield f, c_flags, "\n".join(current)
#             f = m.group(1)
#             c_flags = flags
#             current = [m.group(2).strip()]
#             break
#         if parsing and not m:
#             current.append(line.strip())
#     yield f, c_flags, "\n".join(current)


def load_frs_from_issuetracker():
    issues = _download_issues()
    relevant = filter_relevant_issues(issues)
    all_frs = {(None, 0, "")}
    for v in relevant:
        lines = v.description.splitlines()
        for frs in _extract_frs_lines(lines):
            all_frs.add(frs)
    for i in range(1, KNOWN_WEBFRS_MAX + 1):
        all_frs.add(("3.0WebFRS%03d" % i, 0, ""))
    all_frs.remove((None, 0, ""))
    return all_frs


def _download_issues():
    api = IssuetrackerAPI('issue.pbsbiotech.com', 'nstarkweather', 'kookychemist')
    return api.download_issues("pbssoftware")

def filter_relevant_issues(issues):
    relevant = []
    for v in issues.values():
        if v.sprint_milestone == "3.0" and v.tracker == "Specification" and v.status not in ("Closed", "Rejected"):
            relevant.append(v)
    return relevant


def _xl_child_yes(row, col, n):
    form = '=IF(COUNTIF(%s,"Y")+COUNTIF(%s, "n/a")=(ROW(%s)-ROW(%s)+1), "Y", "")'
    first = row + 1, col
    last = row + n, col
    rstr = cell_range(first, last)
    r1 = cell_str(*first)
    r2 = cell_str(*last)
    return form % (rstr, rstr, r2, r1)


def make_paste_data(root):
    data = [("FRS Number", "Level", "id_test", "Tested", "Is Leaf?", "Is Holdup?")]
    di = data[0].index("Tested") + 1
    for i, node in enumerate(root.iter(), 2):
        f = node.id
        tests = TEST_ITEM_SEP.join(str(i) for i in node.get_tests())
        if node.is_leaf():
            if node.is_tested():
                tested = "Y"
                holdup = ""
            elif node.is_na():
                tested = "n/a"
                holdup = ""
            else:
                tested = ""
                holdup = "Y"
            leaf = "Y"
        else:
            if node.is_na():
                tested = "n/a"
            else:
                tested = _xl_child_yes(i, di, node.total_len())
            leaf = ""
            holdup = ""
            
        if not tests and node.has_children() and node.is_tested():
            tests = "'--"
        
        if f[:3] == "3.0":
            count = 0
        else:
            count = f.count(".")
        data.append((f, count, tests, tested, leaf, holdup))
    return data


TEST_ITEM_SEP = "\n"


def find_cols(ws, *cols):
    first = ws.Cells(1,1)
    last = first.End(xlc.xlToRight)
    headers = ws.Cells.Range(first,last).Value[0]
    res = [headers.index(c) for c in cols]
    return res


def _unit_data(ws):
    cr = ws.Cells.Range
    first = cr("A2")
    last = first.End(xlc.xlDown).End(xlc.xlToRight)
    return cr(first, last).Value
        

def load_unit_test_map(ws):
    data = _unit_data(ws)
    vi, frs, tested = find_cols(ws, "VI", "FRS", "Unit tested?")
    utmap = []
    for row in data:
        v = row[vi]
        f = row[frs]
        t = row[tested].lower() == "yes"
        if v: v = "<UnitTest> " + v
        utmap.append((f, v))
    return utmap


def process_user_tests(xl, root, user_test_matrix):
    user_wb = xl.Workbooks.Open(user_test_matrix)
    user_ws = user_wb.Worksheets(1)
    user_test_map = load_user_test_map(user_ws)
    user_wb.Close(False)
    root_add_test_map(root, user_test_map)
    
    

def process_unit_tests(xl, root, unit_test_matrix):
    if unit_test_matrix is None:
        print("No unit tests provided - skipping")
        return
    unit_wb = xl.Workbooks.Open(unit_test_matrix)
    unit_ws = unit_wb.Worksheets(1)
    unit_test_map = load_unit_test_map(unit_ws)
    root_add_test_map(root, unit_test_map)
    unit_wb.Close(False)
    

def _is_wd(f):
    return f.endswith(".docx") and f[:2] != "~$"
    

def _get_files(path):
    return [pjoin(path, f) for f in os.listdir(path) if _is_wd(f)]
        

def process_one_code_review(doc, root):
    doc_id = None
    frs = []
    for p in doc.Paragraphs:
        split = p.Range.Text.split(":", 1)
        tag = split[0].strip()
        if tag == "Document ID":
            doc_id = split[1].strip()
        elif tag.startswith("FRS"):
            frs.append(tag)
    if not doc_id:
        print("Did not find document ID for %r" % doc.Name)
        return
    items = [(f, doc_id) for f in frs]
    root_add_test_map(root, items)
    

def process_code_reviews(word, root, path):
    if path is None:
        print("No code reviews provided - skipping")
        return
    docs = word.Documents
    files = _get_files(path)
    for f in files:
        doc = docs.Open(f)
        process_one_code_review(doc, root)
    doc.Close(False)
    


def full_frs_tree(user_tests, unit_tests, code_reviews):
    """ 
    :param user_tests: xl document with user tests (from James)
    :param unit_tests: xl document with unit tests (from James)
    :param code_reviews: folder path with 1-N code review documents. 
    """
    print("Downloading FRS items from issuetracker...")
    all_frs_items = load_frs_from_issuetracker()
    reqs = build_frs_tree(all_frs_items)
    
    xl = Excel(visible=False)
    try:
        print("Loading User Test Matrix...")
        process_user_tests(xl, reqs, user_tests)

        print("Loading Unit Test Matrix...")
        process_unit_tests(xl, reqs, unit_tests)
    finally:
        xl.Quit()
        
    word = Word(visible=False)
    try:
        print("Loading Code Review Matrix...")
        process_code_reviews(word, reqs, code_reviews)
    finally:
        word.Quit()
    return reqs
        

def main(user_test_matrix, unit_test_matrix=None, code_review_path=None):
    
    print("Downloading FRS items from issuetracker...")
    all_frs_items = load_frs_from_issuetracker()
    reqs = build_frs_tree(all_frs_items)
    
    xl = Excel()
    with xl_screen_lock(xl):
        print("Loading User Test Matrix...")
        process_user_tests(xl, reqs, user_test_matrix)

        print("Loading Unit Test Matrix...")
        process_unit_tests(xl, reqs, unit_test_matrix)

    word = Word()
    with wd_screen_lock(word):
        print("Loading Code Review Matrix...")
        process_code_reviews(word, reqs, code_review_path)
    word.Quit()

    print("Compiling data for final matrix")
    data = make_paste_data(reqs)
    
    ws = get_matrix_sheet(xl)
    paste_data(ws, data)
    print("Done")


def main2(user_test_matrix, unit_test_matrix=None, code_review_path=None):
    
    print("Downloading FRS items from issuetracker...")
    all_frs_items = load_frs_from_issuetracker()
    reqs = build_frs_tree(all_frs_items)
    
    xl = Excel()
    with xl_screen_lock(xl):
        print("Loading User Test Matrix...")
        process_user_tests(xl, reqs, user_test_matrix)

        print("Loading Unit Test Matrix...")
        process_unit_tests(xl, reqs, unit_test_matrix)

    word = Word()
    with wd_screen_lock(word):
        print("Loading Code Review Matrix...")
        process_code_reviews(word, reqs, code_review_path)
    word.Quit()
    print("Done")
    return reqs
