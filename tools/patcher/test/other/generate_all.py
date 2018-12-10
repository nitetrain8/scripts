import generate_patches

def parse_alarms3():
    alf = "Alarms On.alm"
    fp = os.path.join(generate_patches.getref(), alf)
    with open(fp, 'r') as f:
        _ = f.readline()
        txt = f.read()
    lines = txt.splitlines()
    alarms = set()
    for l in lines:
        alm, _ = l.split(",",1)
        alarms.add(alm)
    return list(alarms)

import random, os
import sys

if len(sys.argv) > 1:
    i = int(sys.argv[1])
else:
    i = 3  # default to generate

def fforce(name):
    n = random.randint(0, 1)
    a = random.randint(0, 1)
    return "%s,%d,%d"%(name, n, a)

import os
here = os.path.dirname(__file__)
d = os.path.join(here, "alarms_patches")

generate_patches.generate1(parse_alarms3(), i, d, 
        "alarms", fforce, 3, 8, True)
