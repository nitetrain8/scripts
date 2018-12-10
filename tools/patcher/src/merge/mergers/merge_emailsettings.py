from collections import OrderedDict
from cfg_compare import Merger

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

class EmailMerger(Merger):
    def parse(self, ff):
        return parse_emails(ff)

    def v2s(self, n, v):
        # if n == "Recipient Email Addresses":
        #     if len(v) > 20:
        #         return "....."
        # if n == "Return Address":
        #     if len(v) > 20:
        #         return "....."
        return str(v)

    def output(self, f):
        return "".join("%s,%s\n"%v for v in f.items())

from file_types import register
register("emailsettings", EmailMerger.run_merge)
