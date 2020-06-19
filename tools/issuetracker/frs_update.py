
from .clientapi import IssuetrackerAPI
from .multithread_pdf_download import download_issues_pdf_multithread
from .update_events import * 

import os
from officelib import wordlib
import dateutil.parser
import dateutil.tz
import datetime
import queue
import threading
import subprocess
import time


FRS_DEFAULT_BOOKMARK_INDEX_TITLE = "FRS Specification Index"


class FRSError(Exception):
    pass

class PDFTKInfoError(FRSError):
    pass


def iter_gantt_outline(gantt):
    seen = set()
    level = 0
    for i in gantt:
        seen.clear()
        p = i
        level = 0
        while True:
            if p in seen:
                raise ValueError("Circular graph detected: %s" % seen)
            seen.add(p)
            p = p.parent
            if p is None:
                break
            level += 1
        yield level, i
                
                
def make_tree2(gantt):
    tree = {}
    seen = set()
    for iss in gantt:
        path = [iss]
        if iss in seen:
            continue
        seen.add(iss)
        p = iss.parent
        while p is not None:
            path.append(p)
            seen.add(p)
            p = p.parent
        v = tree
        while path:
            i = path.pop()
            if i not in v:
                v[i] = {}
            v = v[i]
    return tree


def append_line(lines, lvl, issue, domain, issues):
    link = "https://" + domain + "/issues/%d" % issue.id
    lines.append((lvl, "Issue #%d: %s" % (issue.id, issue.subject), link, issue))
    issues.append(issue)


def parse_tree(tree, lines, domain, level, set_gantt, unmodified, issues):
    for k in sorted(tree, key=lambda iss: iss.id):
        if k not in set_gantt:
            unmodified.add(k)
        append_line(lines, level, k, domain, issues)
        parse_tree(tree[k], lines, domain, level+1, set_gantt, unmodified, issues)
    

def make_style(doc, name="PY_FRS_TITLE", font_size=24, font="Calibri", 
                     alignment=None, indent=None, tabstops=None, space_after=None):
    
    if alignment is None:
        alignment = wordlib.c.wdAlignParagraphCenter
    
    style = doc.Styles.Add(name)
    style.BaseStyle = doc.Styles("Normal")
    style.NoSpaceBetweenParagraphsOfSameStyle = True
    
    style.Font.Size = font_size
    style.Font.Name = font
    
    style.ParagraphFormat.Alignment = alignment
    style.ParagraphFormat.SpaceBeforeAuto = False
    style.ParagraphFormat.SpaceAfterAuto = False
    style.ParagraphFormat.LineSpacingRule = wordlib.c.wdLineSpaceSingle
    
    if indent is not None:
        style.ParagraphFormat.LeftIndent = wordlib.inches_to_points(indent)
    
    if tabstops is not None:
        style.ParagraphFormat.TabStops.Add(wordlib.inches_to_points(tabstops), 
                                           wordlib.c.wdAlignTabLeft, 
                                           wordlib.c.wdTabLeaderDots)
    
    if space_after is not None:
        style.ParagraphFormat.SpaceAfter = space_after
    
    return style

def move(r, n):
    r.MoveStart(wordlib.c.wdCharacter, n)

def add_index_lines(doc, r, lines, unmodified, state):
    styles = {}
    nlines = len(lines)
    for i, (lvl, itxt, href, issue) in enumerate(lines, 1):
        
        state.update(PGS_UPDATE_WORD_INDEX, (i, nlines))
        style_name = "PY_FRS_BODY_%d" % lvl
        style = styles.get(style_name)
        if style is None:
            indent = lvl * 0.1
            style = make_style(doc, style_name, 12, "Calibri", 
                               wordlib.c.wdAlignParagraphLeft, indent, 6, 3)
            styles[style_name] = style
        
        r.Text = itxt
        r.Style = style
        
        if issue in unmodified:
            move(r, len(itxt))
            r.Text = " [unmodified]\t"
            r.Font.Size = 10
            move(r, len(" [unmodified]\t"))
        else:
            r.InsertAfter("\t")
            move(r, len(itxt)+1)
        
        doc.Hyperlinks.Add(r, href, "", href, "Link")
        r.InsertAfter("\r")
        move(r, 20)  # enough for "link"
        doc.Paragraphs.Add()

def create_word_index(lines, doc, index_title, from_date, to_date, unmodified, state):
    
    state.update(PGS_CREATE_WORD_DOC)
    
    pgs = doc.Paragraphs
    
    # title
    r = pgs(1).Range
    r.Text = index_title
    r.Style = make_style(doc, "PY_FRS_TITLE", 24, "Calibri", space_after=0)
    r.InsertAfter("\r")
    
    #subtitle
    move(r, len(index_title) + 2)
    
    # Sanity check from-date and use a different message if we had
    # attempted to export the whole project instead of just filtering.
    # Veronica pointed out that one pdf I gave her had a subtitle that
    # claimed to have all issues from 1/1/1900, which looks silly
    # when vetted by a human. 

    # 2007 is chosen as the start date here because the company was
    # roughly founded in 2007. Since I had to edit this code anyway
    # to accommodate this issue, I can always just edit it again
    # if I need to make a change in the future. 

    if from_date.year < 2007:
        txt = "Updated Specifications for whole project"
    else:
        ds1 = "%d/%d/%d" % (from_date.month, from_date.day, from_date.year)
        ds2 = "%d/%d/%d" % (to_date.month, to_date.day, to_date.year)
        txt = "Updated Specifications from %s to %s" % (ds1, ds2)
    r.Text = txt
    r.Style = make_style(doc, "PY_FRS_SUBTITLE", 12)
    r.InsertAfter("\r")
    
    # index
    move(r, len(txt) + 2)
    add_index_lines(doc, r, lines, unmodified, state)
    

def create_pdf_index(filename, lines, unmodified, index_title, from_date, to_date, state):
    state.update(PGS_BEGIN_PDF_INDEX)
    word = wordlib.Word()
    doc = word.Documents.Add()
    with wordlib.lock_screen(word):
        create_word_index(lines, doc, index_title, from_date, to_date, unmodified, state)
    doc.SaveAs(filename+".docx", wordlib.c.wdFormatXMLDocument)  # docx copy
    doc.SaveAs(filename+".pdf", wordlib.c.wdFormatPDF)
    doc.Close(False)
    return filename+".pdf"
    

def should_include_issue(iss, from_date, to_date):
    # if iss.sprint_milestone != '3.0' or iss.tracker != 'Specification':
    #     return False
    # if from_date is not None:
    #     if iss.updated_on < from_date:
    #         return False
    # if to_date is not None:
    #     if iss.updated_on > to_date:
    #         return False
    # return True
    return (iss.sprint_milestone == '3.0' and 
            iss.tracker == 'Specification' and
            from_date <= iss.updated_on <= to_date)
    
def parse_date(date):
    if isinstance(date, str):
        dt = dateutil.parser.parse(date)
        if dt.tzinfo is None:
            return datetime.datetime(dt.year, dt.month, dt.day, tzinfo=dateutil.tz.tzutc())
        return dt
    return date

def today():
    td = datetime.datetime.today()
    return datetime.datetime(td.year, td.month, td.day, tzinfo=dateutil.tz.tzutc())


def create_outline(gantt, domain, set_gantt):
    lines = []
    issues = []
    tree = make_tree2(gantt)
    unmodified = set()
    parse_tree(tree, lines, domain, 0, set_gantt, unmodified, issues)
    return lines, unmodified, issues


class ProgramState():

    ignore = {
        MPD_IN_PUT,
        MPD_IN_GET,
        MPD_OUT_GET,
        MPD_OUT_PUT,
        MPD_WRITE_COMPLETE,
        PGS_MPD_API_LOGIN,
        PGS_MPD_API_LOGGED_IN,
        PGS_PDFTK_THREAD_DEATH,
    }

    def __init__(self, ignore=None):
        self.ipg_map = None
        self.ipg_flag = threading.Event()
        self.work_thread_failure = threading.Event()
        self.info_oops_lock = threading.Lock()
        self.pdf_info_oops = 0
        self.seen = [0 for _ in state2name]
        self.last = None
        self.last_was_last = False
        if ignore is not None:
            self.ignore = ignore

    def update(self, state, arg=None):
        self.seen[state] += 1

        if state in self.ignore:
            return
        if state == MPD_MAIN_RUNNING:
            done, remaining = arg
            if not done:
                msg = "Downloading %d items ..." % remaining
            else:
                msg = "Downloading (%d/%d)" % (done, remaining)
        elif state == PGS_UPDATE_WORD_INDEX:
            i, nlines = arg
            msg = "Creating index %d of %d" % (i, nlines)
        elif state == PGS_CREATE_WORD_DOC:
            msg = "Creating Word Document..."
        elif state == PGS_BEGIN_PDF_INDEX:
            msg = "Creating PDF Index..."
        elif state == PDFTK_GETTING_INFO:
            msg = "Getting PDF Page Info (%d/%d)" % arg
        elif state == PDFTK_INFO_OOPS:
            if self.seen[state] > 100:
                raise PDFTKInfoError("Exceeded Info Oops Limit.")
        elif state == PGS_LOGGING_IN:
            msg = "Logging into Issuetracker..."
        else:
            n = self.seen[state]
            # hooray variants
            if n < 2:
                n = ""
            msg = "Got update: %s %s" % (state2name[state], n)
        
        if state == self.last:    
            print("\r%s                    " % msg, end="")
        else:
            print()
            print(msg, end="")
        
        self.last = state


def quotify(s):
    return '"%s"' % s

def compile_pdf(src, input_files, path, out_file_name, state):
    
    if not out_file_name.endswith(".pdf"):
        out_file_name += ".pdf"
    
    path = os.path.normpath(path)
    out_file_name = os.path.normpath(out_file_name)
    if not path in out_file_name:
        out_file_name = os.path.join(path, out_file_name)
    input_str = " ".join(quotify(f) for f in input_files)
    toc_ps_path = "%s/%s.ps" % (path, "mk_toc")
    cmd = "gswin64c.exe -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=\"%s\" %s -f %s"
    cmd %= (out_file_name, toc_ps_path, input_str)
    state.update(PGS_BEGIN_BIND_PDF, cmd)
    with open(toc_ps_path, 'w') as f:
        f.write("\n".join(src))
    try:
        code, data = subprocess.getstatusoutput(cmd)
        if code:
            raise ValueError(data)
    finally:
        try:
            os.remove(toc_ps_path)
        except OSError:
            pass
    return out_file_name

def find_pdf_info(fp):
    cmd = "pdftk %s dump_data" % quotify(fp)
    code, data = subprocess.getstatusoutput(cmd)
    if code != 0:
        raise ValueError(data)
    data = data.splitlines()
    it = iter(data)
    npgs = None
    title = None
    while True:
        line = next(it, None)
        if line is None:
            break
        if line == "InfoBegin":
            key = next(it, None)
            val = next(it, None)
            if key is None or val is None:
                raise ValueError("Got corrupt dump file for %s" % fp)
            if key.split(": ")[1] == 'Title':
                title = val.split(": ")[1]
        else:
            try:
                k, v = line.split(": ")
            except ValueError:
                continue
            else:
                if k == 'NumberOfPages':
                    npgs = int(v)
            
    if npgs is None:
        raise ValueError("Failed to find number of pages")
    return title, npgs

def pdf_page_calc_worker(file_q, info_q, state):
    while True:
        args = file_q.get()
        if args is None:
            file_q.task_done()
            break
        fp, iss = args
        try:
            _, npgs = find_pdf_info(fp)
        except ValueError:
            file_q.put((fp, iss))
            with state.info_oops_lock:
                state.pdf_info_oops += 1
            state.update(PDFTK_INFO_OOPS, iss)
        else:
            info_q.put((fp, iss, npgs))
            file_q.task_done()


def make_src(issues, ipg_map, index):
    src = []
    in_files = []
    i = 1
    
    # index is special
    _, npgs = find_pdf_info(index)
    title = FRS_DEFAULT_BOOKMARK_INDEX_TITLE
    prepare_input(i, index, title, src, in_files)
    i += npgs
    
    for iss in issues:
        npgs, fp = ipg_map[iss]
        title = "Issue #%d: %s" % (iss.id, iss.subject)
        prepare_input(i, fp, title, src, in_files)
        i += npgs
    return src, in_files

def prepare_input(i, fp, title, src, in_files):
    ps_toc_template = "[/Page %d /View [/XYZ null null null] /Title (%s) /OUT pdfmark"
    s = ps_toc_template % (i, title)
    src.append(s)
    in_files.append(fp)

def prepare_pdftk(files, state, max_threads=8):
    file_q = queue.Queue()
    info_q = queue.Queue()
    args = (file_q, info_q, state)
    threads = set()
    for _ in range(max_threads): 
        thread = threading.Thread(None, pdf_page_calc_worker, None, args)
        thread.daemon = True
        thread.start()
        threads.add(thread)

    nfiles = 0
    for nfiles, f in enumerate(files, 1):
        file_q.put(f)

    for _ in range(max_threads):
        file_q.put(None)
    state.update(PGS_PDFTK_INFO_BEGIN)
    while threads:
        time.sleep(1)
        for t in list(threads):
            if not t.is_alive():
                threads.remove(t)
        state.update(PDFTK_GETTING_INFO, (info_q.qsize(), nfiles))
    
    if file_q.qsize():
        state.work_thread_failure.set()
        raise PDFTKInfoError("Failed to get all file info!")

    rv = {}
    state.update(PGS_PDFTK_INFO_DONE)
    while True:
        try:
            fp, iss, npgs = info_q.get(False)
        except queue.Empty:
            break
        else:
            rv[iss] = npgs, fp
    return rv   
    

def begin_pdf_processing(api, issues, path, state):
    """ Begin processing pdfs to download in a separate thread. Since 
    this process can take awhile, we multithread + start early. """
    thread = threading.Thread(None, process_pdfs, None, (api, issues, path, state))
    thread.daemon = True
    thread.start()
    return thread
    
def process_pdfs(api, issues, path, state):
    state.update(PGS_BEGIN_PROCESS_PDFS)
    files = download_issues_pdf_multithread(api, issues, path, 8, state)
    ipg_map = prepare_pdftk(files, state, 8)
    state.update(PGS_PROCESS_PDFS_DONE)
    state.ipg_map = ipg_map
    state.ipg_flag.set()
    
    
def main(domain, user, password, project, from_date=None, to_date=None, 
     index_title="FRS Update", pdf_path="pdfs5", index_pdf_name="FRS Update", 
     out_file_name="FRS Update"):

    state = ProgramState()
    
    if from_date is None:
        from_date = datetime.datetime(1900, 1, 1, tzinfo=dateutil.tz.tzutc())
    else:
        from_date = parse_date(from_date)

    if to_date is None or to_date.lower() == "today":
        to_date = today() + datetime.timedelta(days=1)
    else:
        to_date = parse_date(to_date)
        
    state.update(PGS_LOGGING_IN)
    api = IssuetrackerAPI(domain, user, password)
    gantt = list(api.download_issues(project))
    gantt = [i for i in gantt if should_include_issue(i, from_date, to_date)]
    set_gantt = set(gantt)
    
    lines, unmodified, issues = create_outline(gantt, domain, set_gantt)
    pdf_thread = begin_pdf_processing(api, issues, pdf_path, state)
    pdf_fn = os.path.join(pdf_path, index_pdf_name)
    pdf_fn = os.path.abspath(pdf_fn)  # stop MS Word from complaining
    index = create_pdf_index(pdf_fn, lines, unmodified, index_title, from_date, to_date, state)
    
    state.update(PGS_IPG_FLAG_WAITING)
    while not state.ipg_flag.wait(120):
        state.update(PGS_IPG_FLAG_WAITING)
        if not pdf_thread.is_alive():
            if not state.ipg_flag.is_set():
                raise Exception("PDF Download thread unexpectedly died")
            else:
                break
    if not state.ipg_flag.is_set():
        raise Exception("Failed to finish downloading")
    del pdf_thread  # clear references
    state.update(PGS_PREPARE_POSTSCRIPT)
    src, input_files = make_src(issues, state.ipg_map, index)
    
    
    output = compile_pdf(src, input_files, pdf_path, out_file_name, state)
    state.update(PGS_DONE)
    return output