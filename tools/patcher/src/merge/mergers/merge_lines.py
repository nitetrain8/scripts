from cfg_compare import Merger
from collections import OrderedDict

class LineMerger(Merger):
    def parse(self, ff):
        with open(ff, 'r') as f:
            lines = f.read().splitlines()
        return OrderedDict(enumerate(lines,1))

    def output(self, f):
        return "".join(f.values())

from file_types import register
register("linemerge", LineMerger.run_merge)