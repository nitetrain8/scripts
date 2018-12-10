from collections import OrderedDict
from cfg_compare import Merger
from exceptions import SanityError

class LoggerMerger(Merger):

    def sanitycheck(self):
        super().sanitycheck()
        def checkl(f):
            for n, t in f.items():
                if len(t) != 3:
                    raise SanityError("bad tuple for %s: %s"%(n,t))
        checkl(self.nf)
        checkl(self.cf)
        checkl(self.of)

    def post_parse(self):
        force = self.options.force
        nf = self.nf
        for name, v in force.items(): 
            args = v.split(",")
            if len(args) == 3:
                a,b,c = args
            elif len(args) == 2:
                a,b = args
                c   = nf[name][2]
            else:
                raise SanityError("Bad value for 'force' parameter: %s=%s"%(name, v))
            b = b.upper()
            if b != "TRUE" and b != "FALSE":
                raise SanityError("'record?' parameter must be 'TRUE' or 'FALSE': (got '%s' for %s)"%(b, name))    
            force[name] = a.strip(), b.strip(), c

    def parse(self, ff):
        exph = "Data Name\tThreshold change to record\tRecord\tGroup\n"
        with open(ff, 'r') as f:
            header = f.readline()
            if header != exph:
                raise SanityError("File didn't start with the correct line (expected '%s', got '%s')"%(exph, header))
            rv = OrderedDict()
            for var, db, record, group in map(lambda s: s.split("\t"), f.read().splitlines()):
                rv[var] = (db, record, group)
        return rv

    def output(self, f):
        lines = ["Data Name\tThreshold change to record\tRecord\tGroup\n"]
        lines.extend("%s\t%s\t%s\t%s\n"%(name, db, r, g) for name, (db, r, g) in f.items())
        return "".join(lines)

    def v2s(self, n, v):
        db, r, _ = v
        return "%s %s"%(db, r[0])  # deadband + T/F

from file_types import register
register("loggersettings", LoggerMerger.run_merge)