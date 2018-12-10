from collections import OrderedDict
from cfg_compare import Merger
from exceptions import SanityError

def parse_alarms2(f):
    """ The alarms file changed formats 
    from version 1.3(?) to version 3.0.

    It actually changed twice - once to fix a typo,
    and once to change the "ignore" column to notify
    and swap the "audible" and "notify" columns. 
    """
    h = f.readline().lower()
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
    for line in f:
        alm, a,b = line.strip().split(",")
        if v == 2:
            a,b = b,a
            a = "1" if a == "0" else "0"
        alms[alm] = a,b
    return alms
        
def parse_alarms(fp):
    with open(fp, 'r') as f:
        return parse_alarms2(f)
        

class AlarmsMerger(Merger):
    def parse(self, ff):
        return parse_alarms(ff)

    def v2s(self, n, v):
        return "N:%s A:%s"%v

    def post_parse(self):
        force = self.options.force
        for alm, v in force.items():
            a,b = v.split(",")
            force[alm] = a.strip(), b.strip()

    def output(self, f):
        l = ["Name, Notify, Audible\n"]
        l.extend("%s,%s,%s\n"%(name, notify, audible) for name, (notify, audible) in f.items())
        return "".join(l)

    def sanitycheck(self):
        def err_if(c, msg, *args):
            if c: raise SanityError(msg%args)
        def checkv(c):
            for n,v in c.items():
                err_if(not isinstance(v, tuple), "'%s' is not a tuple", v)
                err_if(len(v)!=2, "Bad value: '%s'='%s'", n,v)
                err_if(v[0] not in "10" or v[1] not in "10", "Bad value: '%s'='%s'",n,v)
        checkv(self.cf)
        checkv(self.of)
        checkv(self.nf)
        checkv(self.options.force)


from file_types import register
register("alarms", AlarmsMerger.run_merge)