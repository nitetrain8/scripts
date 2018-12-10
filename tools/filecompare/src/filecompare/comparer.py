import os
from collections import OrderedDict
from exceptions import SanityError
import file_parse

# the way this file uses the formatter 
# class(es) is really sloppy and ugly
# but I don't care enough right now to
# make the code neat. 

class BaseCompareFormatter():
    MIN_COL_WIDTH = 10
    MAX_VAL_WIDTH = 20
    def __init__(self):
        self.lines = []
        self.append = self.lines.append


class FancyFormatter(BaseCompareFormatter):
    def output(self, force=False):
        if not self.lines:
            raise SanityError("Stop that you retard")
        if len(self.lines) == 1 and not force:
            return ""

        mcw = self.MIN_COL_WIDTH
        mxcw = self.MAX_VAL_WIDTH
        widths = [mcw]*len(self.lines[0])
        for row in self.lines:
            if len(row) != len(widths):  # should never happen
                raise SanityError("Irregular line count")
            for i, col in enumerate(row):
                wc = len(col) + 1
                if i > 0:
                    wc = min(mxcw, wc)
                if wc > widths[i]:
                    widths[i] = wc

        rows = iter(self.lines)
        hr = next(rows)

        def _abrv(w, c):
            return "<"+c[:w-6]+"..."+">"
        def _tostr(i,w,c):
            if i == 0:
                return "%-*.*s"%(w,w,c if len(c) < w else _abrv(w,c))
            return "%*.*s"%(w,w,c if len(c) < w else _abrv(w,c))

        header1 = " | ".join(_tostr(i,w,c) for i, (w,c) in enumerate(zip(widths, hr)))
        header2 = "-"*len(header1)
        out = [header1, header2]

        for row in rows:
            s = " | ".join(_tostr(i,w,c) for i, (w,c) in enumerate(zip(widths, row)))
            out.append(s)

        return "\n".join(out)


class CSVFormatter(BaseCompareFormatter):
    def output(self, force=False):
        if not self.lines:
            raise SanityError("Stop that you retard")
        if len(self.lines) == 1 and not force:
            return ""
        return "\n".join(",".join(line) for line in self.lines)

out_fmts = {
    "csv": CSVFormatter,
    "txt": FancyFormatter,
}


def get_out_fmts():
    return set(out_fmts)


class _FileInfo():
    """ File wrapper with some 
    metadata.
    """
    def __init__(self, fp, contents):
        self.fp = fp
        self.fn = os.path.basename(fp)
        self.f = contents

        # pretend to be the ordereddict 
        # we're actually wrapping ... 
        self.items = self.f.items
        self.keys = self.f.keys
        self.values = self.f.values

    def __iter__(self):
        return iter(self.f)

    def __getitem__(self, key):
        return self.f[key]

    def __setitem__(self, key, value):
        self.f[key] = value

    def __delitem__(self, key):
        del self.f[key]

    def __repr__(self):
        return self.f.__repr__()

    def __contains__(self, key):
        return key in self.f


class BaseComparer():
    type="base"
    FormatterFactory = FancyFormatter
    def __init__(self, always_show_names=True, 
                always_show_values=True, err_on_notfound=True, Formatter=None):

        self.always_show_names = always_show_names
        self.always_show_values = always_show_values
        self.err_on_notfound = err_on_notfound
        self.FF = Formatter or self.FormatterFactory
        self.op = self.FF()
        self.ndiffs = 0
        self.report = []

    def compare(self, rfn, *fns):
        self.op = self.FF()
        rf = self.parse(rfn)
        rfi = _FileInfo(rfn, rf)

        hr = [self.type]
        hr.append(rfi.fn)
        files = []
        for fn in fns:
            f = self.parse(fn)
            fi = _FileInfo(fn, f)
            files.append(fi)
            hr.append(fi.fn)
        self.op.append(hr)
        self._compare(rfi, files)
        self.report = self.op.output()
        return self.report

    def parse(self, ff):
        with open(ff, 'r') as f:
            return OrderedDict(enumerate(f.read().splitlines(), 1))

    def output(self):
        return self.op.output()

    def _compare(self, ref, files):
        err_on_notfound = self.err_on_notfound
        always_names = self.always_show_names
        always_values = self.always_show_values

        # iterating in this order makes it
        # easier to build the list of messages
        # without having to transpose col<>row
        # later
        for name, rval in ref.items():
            line = [name, str(rval)]
            dv = False
            for file in files:
                if name not in file:
                    msg = "Reference value '%s' not found in '%s'"%(name, file.fn)
                    if err_on_notfound:
                        raise NameError(msg)
                    else:
                        print("Warning: "+msg)
                        line.append("NotFound")
                        dv = True
                else:
                    fval = file[name]
                    if rval != fval:
                        line.append(str(fval))
                        dv = True
                    elif always_values:
                        line.append(str(fval))
                    else:
                        line.append("")
            if dv:
                self.ndiffs += 1
            if always_names or dv:
                self.op.append(line)


# classes

class AlarmsComparer(BaseComparer):
    type="Alarms"
    def parse(self, ff):
        return file_parse.parse_alarms(ff)

class LVXMLComparer(BaseComparer):
    def parse(self, ff):
        return file_parse.parse_lvxml(ff)

class SysVarsComparer(LVXMLComparer):
    type="System Variables"

class CalFactorsComparer(LVXMLComparer):
    type="Cal Factors"

class EmailSettingsComparer(BaseComparer):
    type="Email Settings"
    def parse(self, ff):
        return file_parse.parse_emails(ff)

class LoggerSettingsComparer(BaseComparer):
    type="Logger Settings"
    def parse(self, ff):
        return file_parse.parse_logger(ff)

class ReportSettingsComparer(BaseComparer):
    type="Report Settings"
    def parse(self, ff):
        return file_parse.parse_reportsettings(ff)

class RecipesComparer(BaseComparer):
    type = "Bioreactor Recipes"
    def parse(self, ff):
        return file_parse.parse_recipes(ff)

class Linecomparer(BaseComparer):
    type = "Lines"
    def parse(self, ff):
        return file_parse.parse_lines(ff)


cmp_types = {
    'alarms': AlarmsComparer,
    'sysvars': SysVarsComparer,
    'calfactors': CalFactorsComparer,
    'emailsettings': EmailSettingsComparer,
    'loggersettings': LoggerSettingsComparer,
    'reportsettings': ReportSettingsComparer,
    'recipes': RecipesComparer,
    'lines': Linecomparer
}

def get_types():
    return set(cmp_types)

def compare(ctype, ref, *files, always_show_names=True,
                always_show_values=True, err_on_notfound=True,
                outfmt="txt", minw=10, maxw=20):
    cls = cmp_types[ctype]
    FC = out_fmts[outfmt]

    # This is a hack because I didn't have the foresight
    # to program configurable column widths in a sensible
    # way, and I'm too lazy to refactor. 
    if outfmt == "txt":
        if maxw < minw:
            raise SanityError("minw(%d) can't be greater than maxw(%d)"%(minw, maxw))
        def factory():
            f = FC()
            f.MAX_VAL_WIDTH = maxw
            f.MIN_COL_WIDTH = minw
            return f
    else:
        factory = FC
    c = cls(always_show_names, always_show_values, err_on_notfound, factory)
    res = c.compare(ref, *files)
    diff = c.ndiffs
    return diff, res
    

def compare2(ctype, ref, *files, always_show_names=False,
                always_show_values=False, err_on_notfound=True,
                outfmt="txt"):
    cls = cmp_types[ctype]
    FC = out_fmts[outfmt]

    # This is a hack because I didn't have the foresight
    # to program configurable column widths in a sensible
    # way, and I'm too lazy to refactor. 
    c = cls(always_show_names, always_show_values, err_on_notfound, FC)
    c.compare(ref, *files)
    return c