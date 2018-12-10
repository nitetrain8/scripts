from cfg_compare import Merger
from collections import OrderedDict

class ReportSettingsMerger(Merger):
    def parse(self, ff):
        with open(ff, 'r') as f:
            lines = f.read().splitlines()
        return OrderedDict(l.split() for l in lines)

    def output(self, f):
        return "".join("%s\t%s\n" % t for t in f.items())

from file_types import register
register("reportsettings", ReportSettingsMerger.run_merge)