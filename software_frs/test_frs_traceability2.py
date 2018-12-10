
import pickle, os, datetime, difflib
from scripts.tools import issuetracker
import inspect


def clear_cache():
    global _tcache
    try:
        os.remove(_cache_file)
    except (FileNotFoundError, NameError):
        pass
    _tcache = None
    _cache = None
    
def setup():
    global IssuetrackerAPI, tests, passed, errors, _cache_file, _tcache
    tests = 0
    passed = 0
    errors = []
    _cache_file = "issues_cache.pkl"
    _tcache = None
    class MockAPI(issuetracker.IssuetrackerAPI):
        
        def __init__(self, *args, **kw):
            super().__init__(*args, login=False, **kw)

        def download_issues(self, *args, _Force=False, **kw):
   
            date, issues, reason = self._load_cache(_cache_file)
            
            if not reason:
                if _Force:
                    reason = "Forced re-cache"
                elif issues is None:
                    reason = "No existing cache found."
                elif date < datetime.date.today():
                    reason = "Old cache: %s < %s" % (date, datetime.date.today())
            
            if reason:
                print("Redownloading issues:", reason)
                issues = super().download_issues(*args, **kw)
                self._cache_issues(_cache_file, issues)
                _tcache = datetime.date.today(), issues
            return issues
        
        def _load_cache(self, file):
                global _tcache
                if _tcache is None:
                    if os.path.exists(file):
                        with open(file, 'rb') as f:
                            try:
                                date, issues = pickle.load(f)
                            except Exception as e:
                                reason = "Error: %s" % str(e)
                            else:
                                _tcache = date, issues
                                reason = ""
                    else:
                        date, issues, reason = None, None, "No Cache Found"
                else:
                    date, issues = _tcache
                    reason = ""
                return date, issues, reason   

        def _cache_issues(self, file, issues):
            date = datetime.date.today()
            with open(file, 'wb') as f:
                ob = (date, issues)
                pickle.dump(ob, f)
    IssuetrackerAPI = MockAPI

            
def fail(msg):
    global tests, errors
    tests += 1
    errors.append(msg)

def success():
    global tests, passed
    tests += 1
    passed += 1
    
def assert_equal(a, b, func=None):
    if a != b:
        if func:
            msg = func(a, b)
        else:
            msg = "%s(): %r != %r" % (inspect.stack()[1].function, a, b)
        fail(msg)
    else:
        success()
        
def get_root():
    all_frs = load_frs_from_issuetracker()
    root = build_frs_tree(all_frs)
    return root

def str_diff(a, b):
    return "\n".join(difflib.Differ().compare([a],[b]))


# In[15]:

###########
# Cleanup 
###########
    
def teardown():
    global IssuetrackerAPI
    IssuetrackerAPI = issuetracker.IssuetrackerAPI
    
def finish():
    teardown()
    print("%d / %d tests passed" % (passed, tests))
    if errors:
        print("Errors found")
        for e in errors:
            print(e)
    else:
        print("Success")


# In[17]:

###########
# Tests 
###########
setup()

def test_root_all_frs():
    all_frs = load_frs_from_issuetracker()
    root = build_frs_tree(all_frs)
    seen = {(v.id, v.flags, v.text) for v in root.iter()}
    if seen != all_frs:
        d1 = {a: (b,c) for a,b,c in seen-all_frs}
        d2 = {a: (b,c) for a,b,c in all_frs-seen}
        l1 = sorted(d1.items())
        l2 = sorted(d2.items())
        for a,b in zip(l1, l2):
            print(a, b)
        fail("test_root_all_frs")
    else:
        success()
test_root_all_frs()

def test_root_lookup():
    all_frs = load_frs_from_issuetracker()
    root = build_frs_tree(all_frs)
    ids = {(v.id, v.flags) for v in root.iter()}
    all_frs_2 = {(a,b) for a,b,_ in all_frs}
    assert_equal(ids, all_frs_2)
    s1 = []
    s2 = []
    for id, flags in ids:
        s1.append((root.lookup(id).id, flags))
        s2.append((id, flags))
    assert_equal(s1, s2)
test_root_lookup()

def test_frs_strings():
    xl = Excel()
    wb = xl.Workbooks.open(test_file_path)
    ws = wb.Worksheets("Sheet1")
    test_map = load_test_map(ws)
    all_frs = load_frs_from_issuetracker()
    frs_strings = {f for f, _ in test_map}
    diff = frs_strings - all_frs
    bad_tests = {}
    for d in diff:
        tests = test_map2.get(d)
        for t in tests:
            bad = bad_tests.get(t, None)
            if bad is None:
                bad_tests[t] = bad = []
            bad.append(d)
    #     print(test_map2.get(d), d)
    for t, frs in sorted(bad_tests.items()):
        print(t, frs)
    if not bad_tests:
        print("No Bad Tests Found")
    else:
        assert False, "Bad Tests found"
        
def test_cleanup():
    canceled_match = re.compile(r"^[ \*\+]*\-.*\-").match
    relevant = download_relevant_issues()
    for v in relevant:
        lines = v.description.splitlines()
        for line in lines:
            if canceled_match(line):
                for match in (_toplevel_match, _subitem_match):
                    m = match(line)
                    if m:
                        print(line, m.groups())
                        break
                else:
                    print(line)
#test_cleanup()

def test_regex_match(s, exp, match, should_match, msg):
    m = match(s)
    if should_match:
        if not m:
            fail(msg)
            return
        assert_equal(m.group(1), exp)
    else:
        assert_equal(m, None)

def test_canceled(s, exp, match=True):
    test_regex_match(s, exp, _canceled_match, match, 
                     "%r did not match canceled regex" % s)


exp = "FRS123.4"
test_canceled("* -*FRS123.4*: bob-", exp)
test_canceled("* -*FRS123.4*-: bob", exp)
test_canceled("* -*FRS123.4*:- bob", exp)
#test_canceled("* -*FRS123.4-*: bob")
test_canceled("* *FRS123.4*: bob", exp, False)

def test_child_yes(r, c, n, exp):
    
    def on_err(a,b):
        err = "test_child_yes"
        err += "(%s, %s, %s):\n"%(r,c,n) + str_diff(a,b)
        return err
    res = _xl_child_yes(r,c,n)
    assert_equal(exp.lower(), res.lower(), on_err)
    
test_child_yes(758, 4, 4, 
               '=if(countif(D759:D762,"Y")+countif(D759:D762, "n/a")=(ROW(D762)'
               '-ROW(D759)+1), "Y", "")')


def test_extract_frs_line(line, exp, exp_flag):
    
    def on_err(a,b):
        return "extract_frs_line(%r):\n%s" % (line, str_diff(str(a),str(b)))
    
    frs = _extract_frs_line(line)
    assert_equal(frs, (exp, exp_flag, line), on_err)
    
def test_key_match(s, exp):
    res = _key_match(s)
    assert_equal(res, exp)
    
test_key_match("FRS123.4.5.6", ("FRS123", "4.5.6"))
test_key_match("FRS123", ("FRS123", ""))
test_key_match("3.0WebFRS123.4.5", ("3.0WebFRS123", "4.5"))
test_key_match("3.0WebFRS123", ("3.0WebFRS123", ""))
test_key_match("FDS_SFW_pHControlManualMode", ("FDS_SFW_pHControlManualMode", ""))
    
    
test_extract_frs_line("*+FRS1234+*", "FRS1234", 0)
test_extract_frs_line("* *FRS1234.1:*", "FRS1234.1", 0)
test_extract_frs_line("* -*FRS123.4*: bob-", "FRS123.4", FRS_NA)
test_canceled("* -*FRS123.4*-: bob", "FRS123.4", FRS_NA)
test_canceled("* -*FRS123.4*:- bob", "FRS123.4", FRS_NA)
    
finish()
