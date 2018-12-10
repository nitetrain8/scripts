import configparser
import os

# sanity check routines
def _error(n, m):
        print("ERROR '%s': %s"%(n,m))
        return 1

def _isstr(o,n, isf):
    v = getattr(o, n)
    if not isinstance(v, str) or v == "":
        return _error(n, "must be non-empty str")
    if isf and not os.path.exists(v):
        return _error(v, "path not found")
    return 0

def _oneof(o, n, p):
    v = getattr(o, n)
    if v not in p:
        return _error(n, "must be one of "+", ".join(p))
    return 0

def _excl_set(o, a , b):
    v1 = getattr(o, a)
    v2 = getattr(o, b)
    for n in v1:
        if n in v2:
            return _error("%s/%s"%(a,o), "overlapping sets")
    return 0

def _excl_dict_set(o, a , b):
    v1 = set(getattr(o, a))
    v2 = getattr(o, b)
    for n in v1:
        if n in v2:
            return _error("%s/%s"%(a,o), "overlapping sets")
    return 0

def _nnvals(o,a):
    v = getattr(o,a)
    for key, val in v.items():
        if val is None:
            return _error(a, "values cannot be None: %s"%key)
    return 0

_patch_template = """
# Note - EVERYTHING IS CASE SENSITIVE!
# The parser will attempt to sanity check everything
# but be careful anyway!

# Note - whenever the structure of a config file
# is naturally represented using a hierarchy of 
# nested structures (System Variables, Cal Factors...),
# the name of each variable below should be a dotted
# name path (Agitation.Minimum (RPM), etc). 

# Force a setting to specific value.
# Use strings "New" or "User" to 
# force the merge parser to always
# use the New reference or User's 
# value, respectively. Functionally
# Equivalent to the "New" and "User"
# fields below. 

[Force Raw Value]
%(raw)s

# Always use the new Default

[Force New Value]
%(new)s

# Always use User Value

[Force User Value]
%(user)s

# Todo - add options for reference files
# and determining User's PBS version number

# General options
# Type values: sysvars TODO: alarms, loggersettings
# Output path is relative to caller's path, not EXE's 
# patch file's!

[General]
Type=%(type)s
Output=.\{filename}
Logfile=.\{filename}merge log.txt

# Translation table for names which have changed
# Old Name -> New Name

[Translate]
%(translate)s

# Old variables that are no longer relevant (not renamed!)
# For documentation purposes only.

[Depreciated]
%(depreciated)s

# New variables (NOT renamed!) 
# For documentation purposes only.

[New Variables]
%(newvars)s
"""

class Options():
    def __init__(self):
        self.type = "<unknown>"
        self.use_new = set()
        self.use_user = set()
        self.force = {}
        self.translate_new = {}
        self.translate_old = {}
        self.cff = ""
        self.nff = ""
        self.off = ""
        self.outf = ""
        self.depreciated = set()
        self.newvar = set()
        self.logfile = ""
        self.verbose = False
        self.v = None
        self.other = []

    def _dstr(self):
        print("Options Dump:")
        for k,v in self.__dict__.items():
            if isinstance(v, (dict, set)):
                print("    %s: %s"%(k, "{...}"))
            else:
                print("   %s: %s"%(k,v))

    def sanitycheck(self, types):
        """ High level sanity check on basic options.
        Individual routines will perform more rigourous
        sanity checking of specific variable names, etc. 
        """    
        v = 0
        v += _oneof(self, "type", types)
        v += _isstr(self, "cff", True)
        v += _isstr(self, "nff", True)
        v += _isstr(self, "off", True)
        v += _isstr(self, "outf", False)

        # These checks verify there are no mutually exclusive
        # options. The sanity checks managed by the Merger
        # class run later and verify that the variable
        # names themselves match the corresponding file
        # contents. 

        v += _excl_dict_set(self, "force", "use_new")
        v += _excl_dict_set(self, "force", "use_user")
        v += _excl_set(self, "use_new", "use_user")

        v += _nnvals(self, "force")
        return v == 0

    def create_patch_string(self):
        fmt = {
            "raw": "\n".join("%s=%.5f"%t for t in self.force.items()),
            "new": "\n".join(self.use_new),
            "user": "\n".join(self.use_user),
            "translate": "\n".join("%s=%s"%(old, new) for new, old in self.translate_new.items()),
            "depreciated": "\n".join(self.depreciated),
            "newvars": "\n".join(self.newvar),
            "type": self.type,
        }
        return _patch_template%fmt
        
        
def parse_config(fn, other=None):
    
    # optionxform transforms the parsed string
    # into the value used internally.
    # Setting it to str here forces everything to be
    # case sensitive. 
    
    c = configparser.ConfigParser(allow_no_value=True,
                                  interpolation=configparser.Interpolation())
    c.optionxform = str
    
    with open(fn, 'r') as f:
        c.read_file(f)

    # check for empty file and bail early
    lc = list(c)
    if len(lc) == 1 and lc[0] == 'DEFAULT':
        return Options()
    
    use_new       = set()
    use_user      = set()
    force         = {}
    translate_new = {}
    translate_old = {}
    depr          = set()
    newvar        = set()

    for option in c['Force New Value']:
        use_new.add(option)
    
    for option in c['Force User Value']:
        use_user.add(option)
        
    for option, value in c['Force Raw Value'].items():
        if value == "New":
            use_new.add(option)
        elif value == "User":
            use_user.add(option)
        else:
            force[option] = value
    
    for oldname, newname in c['Translate'].items():
        translate_new[newname] = oldname
        translate_old[oldname] = newname

    for option in c['Depreciated']:
        depr.add(option)

    for option in c['New Variables']:
        newvar.add(option)
            
    ftype   = c['General']['Type']
    output  = c['General']['Output']
    logfile = c['General']["Logfile"]

    # these aren't used when the program goes
    # through the CLI, but allowing them as options
    # can help test files to be easier to write
    # by embedding these values directly in the .patch.

    cff     = c['General'].get('User File', "")
    off     = c['General'].get('Old Defaults', "")
    nff     = c['General'].get('New Defaults', "")
    verbose = c['General'].get('Verbose', "")
    
    o               = Options()
    o.type          = ftype
    o.use_new       = use_new 
    o.use_user      = use_user
    o.force         = force
    o.translate_new = translate_new
    o.translate_old = translate_old
    o.outf          = output
    o.depreciated   = depr
    o.newvar        = newvar
    o.logfile       = logfile
    o.cff           = cff
    o.off           = nff
    o.nff           = off
    o.verbose       = verbose
    o.other         = other or []

    return o