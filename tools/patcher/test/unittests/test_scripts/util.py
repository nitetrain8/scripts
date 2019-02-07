
"""
Utilities and common file paths, etc for
test fixtures.

Primary use case is loading all test data
from the data folder. 
"""

import os
import configparser
import shutil
import subprocess
import sys

from time import sleep

_DN = os.path.dirname

HERE = _DN(__file__)
PATCHER = _DN(_DN(_DN(HERE)))
SRC = os.path.join(PATCHER, "src")
MERGE = os.path.join(SRC, "merge")
SCRIPT = os.path.join(MERGE, "merge.py")
EXE = os.path.join(PATCHER, "builds", "merge.exe")
DATA = os.path.join(_DN(HERE), "data_files")
TMP  = os.path.join(DATA, "tmp")
PYTHON = sys.executable

sys.path.append(SRC)
sys.path.append(MERGE)


# clean old test files
if os.path.exists(TMP):
    shutil.rmtree(TMP)
os.makedirs(TMP, exist_ok=True)


##################################
# Command line helpers
##################################

# MERGE_CMD must be set by conftest.py
# to the EXE file path or to e.g. "python merge.py"
MERGE_CMD = None


def quote(s):
    return '"%s"'%s

def set_run_cmd(c):
    """
    Used by conftest.py to set whether the suite
    is run in python mode or EXE mode. 
    """
    global MERGE_CMD
    MERGE_CMD = c

def make_command(*args, **kw):
    """
    Create the command line. I'm sure there's a module or something
    that does most of this.  
    """
    if MERGE_CMD is None:
        raise ValueError("MERGE_CMD not initialized")
    cmdl = [MERGE_CMD]
    for s in args:
        if " " in s and not (s[0] == s[-1] == '"'):
            s = quote(s)
        cmdl.append(s)

    # make_command(foo='bar') -> '--foo=bar'
    for k, v in kw.items():
        if not k.startswith("-"):
            k = "--" + k
        if v is not None and v != "":
            cmdl.append("%s=%s"%(k,v))
        else:
            cmdl.append(k)
    return " ".join(cmdl)

def cmd(c, check=False, shell=False, **kw):
    return subprocess.run(c, check=check, shell=shell, **kw)

def _cmd2(c, shell=False, **kw):
    print("-"*30)
    print("CMD:", c)
    rv = subprocess.Popen(c, shell=shell, **kw)
    print("-"*30)
    return rv

CREATE_NEW_CONSOLE = 0x10

def _cmd3(c, cwd, **kw):
    """ starts an independent process """
    _cmd2(c, shell=False, stdin=None, stderr=None, stdout=None, close_fds=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|CREATE_NEW_CONSOLE, cwd=cwd, **kw)


##################################
# TestInfo and loading
##################################

def load_test_cases(type):
    """
    Primary test loading function. Used to find test
    cases following the standard directory format of
    Data folder/[type]_case_files/case_[name]
    """
    dn = type + "_case_files"
    dn = os.path.normpath(dn)
    path = os.path.join(DATA, dn)
    folders = os.listdir(path)
    return [load_case_normal(os.path.join(path, f), type) for f in folders if f.startswith("case_")]


def load_case_by_name(type, name):
    """
    Similar to above, but load a specific test case. 
    Does not require any special formatting of the test case name.
    """
    dn = type+"_case_files"
    path = os.path.join(DATA, dn, name)
    return load_case_normal(path, type)

import glob
def load_cases_glob(pathname, type="none"):
    """
    Similar to above in that it allows loading test cases by
    specific name, but allows the user to load cases matching
    the given glob. 
    """
    path = os.path.join(DATA, pathname)
    def j(f): return os.path.join(path, f)
    return [load_case_normal(j(f), type) for f in glob.glob(path)]


def load_file(fp):
    with open(fp, 'r') as f:
        return f.read()

class TestInfo():
    """
    Test class to load and run the merge test. Contains attributes and 
    methods to facilitate the process of running the test and finding 
    the associated files. Also has a name field to simplify debugging of
    failures.  
    """

    verbose = False
    def __init__(self, patch, cff, off, nff, exp, result, name, basepath):
        self.patch = patch
        self.cff = cff
        self.nff = nff
        self.off = off
        self.expected = exp
        self._default_output = result
        self.kw = {}
        self._outf_from_file, self.logfile = self.find_output()
        self.result = self._outf_from_file or result
        self.name = name
        self.path = basepath
        self.rv = 0

    def get_cmd(self):
        """
        Return the command line arguments for the test case
        to be run from subprocess.Popen() (or equivalent).
        """
        kw = self.kw.copy()

        # else, output is handled in patch file already
        if not self._outf_from_file:
            kw['--outf'] = self._default_output

        if self.verbose:
            kw['--verbose'] = None

        # it should be fine just to wrap stuff in quotes ...
        return make_command(self.patch, self.cff, self.off, self.nff, **kw)

    def find_output(self):
        """ Find the name and location of the output of
        merge.exe based on the supplied TestInfo.

        Note - path calculation MUST match the logic used
        by merge/parse_config.py and merge/merge.py !!!
        """
        c = configparser.ConfigParser(allow_no_value=True)
        c.optionxform = str
        
        with open(self.patch, 'r') as f:
            c.read_file(f)

        outf = c['General']['Output'].format(filename=os.path.basename(self.cff))
        log  = c['General']['Logfile'].format(filename=os.path.basename(self.cff))
        if "--outf" in self.kw:
            outf = self.kw['--outf']

        if outf or log:
            # the path calculation is based on relative path for 
            # the merge.exe logic, but in unittesting we force
            # the output to be to the TMP directory. 
            here = os.path.abspath(".")
            os.chdir(TMP)
            if outf:
                p = os.path.abspath(outf)
            else:
                p = ""
            if log:
                p2 = os.path.abspath(log)
            else:
                p2 = ""
            os.chdir(here)
            return p, p2
        else:
            return "", ""
            

    def __repr__(self):
        return "<%s: %s>"%(self.__class__.__name__, self.name)

    def cleanup(self):
        self.cleanup_output()

    def cleanup_output(self):
        for f in (self.result, self.logfile):
            if os.path.exists(f):
                os.remove(f)

    def run_merge(self):
        """ Fix the path names up to be more clear.
        The logic in merge.py is used to keep names
        similar when migrating user files, but
        here we're more interested in renaming after
        the name of the case.
        """
        self.rv = cmd(self.get_cmd())
        dn = os.path.dirname(self.result)
        ext = os.path.splitext(self.result)[1]
        nr = os.path.join(dn, self.name+ext)
        nl = os.path.join(dn, self.name+os.path.splitext(self.logfile)[1])

        for file in (nr, nl):
            try:
                os.remove(file)
            except FileNotFoundError:
                pass
                
        # these might not exist if the script 
        # throws an exception before writing output. 
        if os.path.exists(self.result):
            os.rename(self.result, nr); self.result = nr
        if os.path.exists(self.logfile):
            os.rename(self.logfile, nl); self.logfile = nl

def load_case_normal(path, typ):
    patch    = None
    off      = None
    cff      = None
    nff      = None
    expected = None

    def dup(m):
        raise ValueError("multiple %s in test directory: %s"%(m,path))
    def notnone(v,n):
        if v is None:
            raise FileNotFoundError("%s file not found in %s"%(n, path))

    # Loop through files and assign to the correct type according to name
    # Perform some sanity checking to make sure no multiples correspond 
    # to the same type. 
    for file in os.listdir(path):
        if file.endswith(".patch"):
            if patch is None:
                patch = file
            else:
                dup('patches')
        elif file.startswith("new_"):
            if nff is None:
                nff = file
            else:
                dup('new default files')
        elif file.startswith("old_"):
            if off is None:
                off = file
            else:
                dup('old default files')
        elif file.startswith("user_"):
            if cff is None:
                cff = file
            else:
                dup('user files')
        elif file.startswith("expected_"):
            if expected is None:
                expected = file
            else:
                dup('expected files')
        else:
            pass  # allow other files e.g. readmes 

    notnone(patch, "Patch")
    notnone(off,   "Old default")
    notnone(cff,   "User file")
    notnone(nff,   "New default")

    # The default output file, if not specified in the patch file,
    # should go in the data_files folder

    case = os.path.basename(path)
    name = "%s.%s" % (typ, case)
    name = name.replace("\\", ".")
    outfn = name + ".result"
    outfp = os.path.join(TMP, outfn)
    return TestInfo(os.path.join(path, patch), 
                    os.path.join(path, cff), 
                    os.path.join(path, off), 
                    os.path.join(path, nff),
                    os.path.join(path, expected),
                    outfp, name, path) 


##################################
# Universal Comparison Functions
##################################

import difflib
def diff2(a,b):
    if isinstance(a, str):
        a = a.splitlines()
    if isinstance(b, str):
        b = b.splitlines()

    # inserting a blank line here here doesn't impact
    # any real use case, but ensures that the message printed
    # by pytest's assert failure thingy 
    res = [""]
    res.extend(s.strip() for s in difflib.ndiff(a,b) if s[0] in ("+", "-", "?", "!"))
    return res

def diff(a,b):
    return "\n".join(diff(a,b))

def diff3(a,b):
    """
    Simple wrapper for diff2 that returns a simple error message if
    no diff is found. This occurs when a string difference is found,
    but a processed file difference is not. For example, this can 
    occur due to differences in string representation of floating 
    points: 0.001 vs 0.0010. 
    """
    res = diff2(a,b)
    if len(res) == 1 and res[0] == "":  # no diff found
        return ["<Unknown mismatch - processed files are identical. Compare raw text>"]
    return res

# using the stringwrapper class lets us easily
# hook the repr output on assertion failures using
# the hook defined in conftest.py 

# the default string compare isn't very useful for
# running the type of line diff that we need
# here, so an ugly wrapper and a helper function 
# are needed.

# the "parse" function should accept the string and
# return the list of lines- the default is str.splitlines().
# This callback lets some files like e.g. system variables
# run the comparison by file compare, but have the assert
# output run on a processed string that results in more human-
# readable output. 

def file_compare(exp, res, parse=None):
    __tracebackhide__ = True  # tell pytest to skip this in the traceback
    if parse is None:
        def parse(s):
            return s.splitlines()
    assert StringWrapper(exp, parse) == StringWrapper(res, parse)  # simple

def raise_assert(msg):
    """ Raise an assertion error using the 
    list of lines provided in 'msg' as the 
    message. 

    Note the code in conftest.py 
    to see how the message is transfered.
    
    Function 'pytest_assertrepr_compare' 
    checks the value of the left argument's
    'goddamnit' attribute (set by __init__)
    and uses that as the custom message
    """
    __tracebackhide__ = True
    assert LinesAsserter(msg) == LinesAsserter()

import abc
class CustomAsserter(abc.ABC):

    def __eq__(self, other):
        return False

    @abc.abstractmethod
    def getlines(self):
        return []

    @abc.abstractmethod
    def getraw(self):
        return ""

class StringWrapper(CustomAsserter):
    def __init__(self, s, parse):
        self.s = s
        self.parse = parse

    def getraw(self):
        return self.s

    def getlines(self):
        return self.parse(self.s)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.s == other.s

class LinesAsserter(CustomAsserter):
    def __init__(self, gd=()):
        self.goddamnit = gd

    def getlines(self):
        return self.goddamnit

    def getraw(self):
        return self.goddamnit
