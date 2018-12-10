import lv_parse
from collections import OrderedDict
from exceptions import SanityError

def parse_lvxml(ff):
    LV = lv_parse.fromfn(ff)
    d = lv_parse.flatten(LV)
    d.LV = LV
    return d


def parse_emails(fp):
    with open(fp, 'r') as f:
        lines = f.read().splitlines()
    emails = OrderedDict()
    for l in lines:
        # There's exactly 1 line in this file that doesn't obey
        # "key,value" format (uses "header1,header2,header3" even though
        # there's only 2 columns for each alarm thing.........)
        key, val = l.split(",",1)
        emails[key] = val
    return emails


def parse_alarms(fp):
    """ The alarms file changed formats 
    from version 1.3(?) to version 3.0.

    It actually changed twice - once to fix a typo,
    and once to change the "ignore" column to notify
    and swap the "audible" and "notify" columns. 
    """
    with open(fp, 'r') as f:
        h = f.readline().lower()
        lines = f.read().splitlines()

    h = tuple(s.strip() for s in h.split(","))
    h2_1 = ("name", "audable", "ignore")
    h2_2 = ("name", "audible", "ignore")
    if h == h2_1 or h == h2_2:  
        v = 2
    elif h == ("name", "notify", "audible"):
        v = 3
    else:
        raise ValueError("Couldn't determine version: %s"%(repr(h)))
    alms = OrderedDict()
    for line in lines:
        alm, a,b = line.strip().split(",")
        if v == 2:
            a,b = b,a
            a = "1" if a == "0" else "0"
        alms[alm] = "N:%s A:%s"%(a,b)
    return alms


def parse_logger(ff):
    exph = "Data Name\tThreshold change to record\tRecord\tGroup\n"
    with open(ff, 'r') as f:
        header = f.readline()
        if header != exph:
            raise SanityError("File didn't start with the correct line (expected '%s', got '%s')"%(exph, header))
        rv = OrderedDict()
        for var, db, record, _ in map(lambda s: s.split("\t"), f.read().splitlines()):
            rv[var] = "%s  %s"%(db, record[0])
    return rv


def parse_reportsettings(ff):
    with open(ff, 'r') as f:
        lines = f.read().splitlines()
    return OrderedDict(l.split() for l in lines)

def parse_lines(ff):
    with open(ff, 'r') as f:
        lines = f.read().splitlines()
    return OrderedDict(enumerate(lines, 1))


class Recipe():
    def __init__(self, name, steps):
        self.name = name
        self.steps = steps

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.name == other.name and self.steps == other.steps

def parse_recipes(ff):
    with open(ff, 'r') as f:
        recipes = f.read().split("\n\n")
    rs = OrderedDict()
    for r in recipes:
        if not r:
            continue
        lines = r.splitlines()
        func, name = lines[0].split(" ", 1)
        if func != "Func":
            raise ValueError(r)
        rs[name] = Recipe(name, lines[1:])
    return rs