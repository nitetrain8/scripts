import util
import pytest

infos = util.load_test_cases("emailsettings")
ids = [i.name for i in infos]

@pytest.mark.parametrize("info", infos, ids=ids)
def test_email_merge_basic(info):
    info.run_merge()
    exp = util.load_file(info.expected)
    res = util.load_file(info.result)
    util.file_compare(exp, res)
    info.cleanup()