from cfg_compare import LVXMLMerger

class SysVarsMerger(LVXMLMerger):
    pass

from file_types import register
register("sysvars", SysVarsMerger.run_merge)