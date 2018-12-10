from cfg_compare import LVXMLMerger

class CalFactorsMerger(LVXMLMerger):
    pass

from file_types import register
register("calfactors", CalFactorsMerger.run_merge)