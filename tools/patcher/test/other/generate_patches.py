"""
Code to generate patches for testing purposes. 

This file contains templates and routines. 
"""

mag3_ref = 'C:\\Users\\Nathan\\Documents\\Dropbox\\Python\\jpnotebooks\\Sessions\\cfg_merge\\patcher\\test\\IM00226 Rev B\\Mag 3'
def getref():
    return mag3_ref


template = """
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
Type=alarms
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


# def parse_alarms3():
#     alarms = "Alarms On.alm"
#     fp = os.path.join(mag3_ref, alarms)
#     with open(fp, 'r') as f:
#         header = f.readline()
#         txt = f.read()
#     lines = txt.splitlines()
#     alarms = set()
#     for l in lines:
#         alm, _ = l.split(",",1)
#         alarms.add(alm)
#     return alarms

def shuffle(l):
    return random.shuffle(l)

def random_force(lst, force, mi, ma):
    def randl(a,b):
        nonlocal lst
        l = random.randint(a,b)
        r = lst[-l:]
        lst = lst[:-l]
        return r
    def random_new_or_user():
        return "\n".join(randl(mi,ma))

    def random_forcei():
        f = []
        for l in randl(mi,ma):
            f.append(force(l))
        return "\n".join(f)

    shuffle(lst)
    force = random_forcei()
    new = random_new_or_user()
    user = random_new_or_user()

    return force, new, user


def generate1(lst, nfiles, pth, typ, fforce, min_force, max_force, kill=False):
    n = 1
    s = set(os.listdir(pth))
    for _ in range(nfiles):
        raw, new, user = random_force(lst, fforce, min_force, max_force)
        fn = "test%d.%s.patch"%(n, typ)
        if not kill:
            while fn in s:
                n += 1
                fn = "test%d.%s.patch"%(n, typ)
        else:
            n += 1
        s.add(fn)
        fp = os.path.join(pth, fn)
        generate2(fp, raw, new, user, "", "", "")


def generate2(outfp, raw, new, user, translate, depreciated, newv):
    os.makedirs(os.path.dirname(outfp), exist_ok=True)

    fmt = {
        "raw": raw,
        "new": new,
        "user": user,
        "translate": translate,
        "depreciated": depreciated,
        "newvars": newv
    }
    s = template%fmt
    print("Creating", outfp)
    with open(outfp, 'w') as f:
        f.write(s)


import random, os