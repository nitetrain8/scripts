import util
import pytest
import os


def load_cases(infos):
    for info in infos:
        files = os.listdir(info.path)
        settings = [f for f in files if f.startswith("loggersettings")]
        if len(settings) > 1:
            pytest.skip("Multiple logger settings files found", allow_module_level=True)
        else:
            fp = '"%s"'%os.path.join(info.path, settings[0])
            info.kw['--loggersettings'] = fp
    return infos


baseinfos = util.load_test_cases("recipes")  
infos = load_cases(baseinfos)
ids = [i.name for i in infos]

@pytest.mark.parametrize("info", infos, ids=ids)
def test_recipe_merge_basic(info):
    if info.verbose:
        print("")  # fixes display for later...
    info.run_merge()
    assert info.rv.returncode == 0, "Script Error"
    exp = util.load_file(info.expected)
    res = util.load_file(info.result)
    util.file_compare(exp, res)
    info.cleanup()


sinfos = load_cases(util.load_cases_glob("recipes_case_files\\sanity_check*", 'recipes'))
sids = [i.name for i in sinfos]

def RC(c):
    """ convert i32 to u32 value
    for the negative return codes
    """
    return (1<<32)+c

@pytest.mark.parametrize("info", sinfos, ids=sids)
def test_recipe_sanity_fail(info):
    info.run_merge()
    assert info.rv.returncode == RC(-3)


igninfos = load_cases(util.load_cases_glob("recipes_case_files\\ignoredel*", 'recipes'))
ignids = [i.name for i in igninfos]

@pytest.mark.parametrize("info", igninfos, ids=ignids)
def test_recipe_ignoredel(info):
    info.kw["--ignore-deleted"] = None
    info.run_merge()
    assert info.rv.returncode == 0, "Script Error"
    exp = util.load_file(info.expected)
    res = util.load_file(info.result)
    util.file_compare(exp, res)
    info.cleanup()


# tests for the --never-ignore option always use one of the recipe names listed below. 

infos = load_cases(util.load_cases_glob("recipes_case_files\\noignoredel*", 'recipes'))
ids = [i.name for i in infos]

@pytest.mark.parametrize("info", infos, ids=ids)
def test_recipe_ignoredel(info):
    info.kw["--ignore-deleted"] = None
    info.kw["--never-ignore"] = "IntegrityTest;TestRecipe1;TestRecipe2;TestRecipe3"
    info.run_merge()
    assert info.rv.returncode == 0, "Script Error"
    exp = util.load_file(info.expected)
    res = util.load_file(info.result)
    util.file_compare(exp, res)
    info.cleanup()