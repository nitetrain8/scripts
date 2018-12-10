
import subprocess
import os
import util
import sys
from util import HERE, PATCHER, MERGE, SCRIPT, EXE, PYTHON



def _age(file):
    try:
        return os.stat(file).st_mtime_ns
    except FileNotFoundError:
        return 0


def _search_age_r(fp, age):
    result = False
    files = os.scandir(fp)
    try:
        for en in files:
            if en.is_dir():
                if en.name != "__pycache__":
                    if _search_age_r(en.path, age):
                        result = True
                        break
            else:
                if en.stat().st_mtime_ns > age:
                    result = True
                    break
    finally:
        # apparently this only exists on python >= 3.6
        if hasattr(files, 'close'):
            files.close()
    return result


def _build():
    bdb = os.path.join(PATCHER, "build.bat")
    util.cmd(bdb)

def _build_exe_if_old():
    exe_age = _age(EXE)
    print("EXE mode specified, verifying EXE is up to date...")
    if _search_age_r(MERGE, exe_age):
        print("Rebuilding EXE by running build.bat")
        _build()
    else:
        print("Skipping rebuild.")


# For debugging pytest options...
def _pd(o):
    for attr in dir(o):
        if not attr.startswith("_"):
            v = getattr(o, attr)
            print("%s = %r"%(attr, v))

def pytest_configure(config):
    global PYTHON

    if config.option.pyexe:
        PYTHON = config.option.pyexe

    if config.option.exe:
        util.set_run_cmd(util.quote(EXE))
        _build_exe_if_old()
    else:
        util.set_run_cmd('%s %s'%(util.quote(PYTHON), util.quote(SCRIPT)))

    if config.option.m_verbose:
        util.TestInfo.verbose = True

def pytest_addoption(parser):
    parser.addoption("--exe", action="store_true")
    parser.addoption("--pyexe")
    parser.addoption("--m_verbose", action="store_true")


_olddir = os.path.abspath(".")

def pytest_runtest_setup(item, nextitem=None):
    global _olddir
    _olddir = os.path.abspath('.')
    os.chdir(util.TMP)

def pytest_runtest_teardown(item, nextitem):
    if nextitem is None:
        os.chdir(_olddir)

# This function is really obnoxious to write
# because half the logic lives in the util file
# and the other half lives here, so the code has
# to be able to do everything it needs to do just
# by importing util and getting functions or attrib
# from CustomAsserter. 

# as the test suite grows, this function grows ever
# more hacky to allow messages from comparison
# functions to deliver pretty assert failure messages

# Currently, the function looks for two subclasses of
# util.CustomAsserter of the SAME type (don't be a retard
# and mix classes), and if the operator is '=='.
# Otherwise, bail. 
# Then, it checks to see if the left argument has 
# attribute 'goddamnit'. If it does, that value is 
# used as the assert message (must be list of lines!)
# otherwise, util.diff3 is used. 

def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, util.CustomAsserter) and isinstance(right, util.CustomAsserter) and type(left) == type(right):
        if op == "==":
            if hasattr(left, "goddamnit"):
                return left.goddamnit
            else:    
                res = util.diff3(left.getlines(), right.getlines())
                if len(res) == 1 and res[0].startswith("<"):
                    res = ["<No mismatched on parsed file - see raw diff below"]
                    res.extend(util.diff3(left.getraw().splitlines(), right.getraw().splitlines()))
                return res
        else:
            raise ValueError(op + " unsupported")  # nameerror
    else:
        return None

def pytest_ignore_collect(path, config):
    """ Use this hook to implement performing
    tests only for certain file types etc.
    """
    return False