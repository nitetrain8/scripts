
# coding: utf-8

import tempfile
import subprocess
import os
from os.path import join as path_join
# jupyter path hack...
import sys
sys.path.append("C:\\users\\nathan\\documents\\dropbox\\python\\scripts\\tools\\filecompare\\src\\filecompare")
from comparer import compare as file_compare

DRIVE = os.path.splitdrive(sys.executable)[0]+"\\"
IQ_DIR = os.path.join(DRIVE, "IQOQ_3L_Mag")
IQ_FILES_DIR = IQ_DIR  # update per customer??
LOG_DIR = os.path.join(IQ_DIR, "log")
CONFIG_FILES_DIR = os.path.join(IQ_DIR, "config_file_references")
FIREWALL_DIR = os.path.join(IQ_DIR, "FirewallSettings")
LV_DIR = "C:\\pbs\\LabVIEW Data\\"


def get_ref(*paths):
    return os.path.join(CONFIG_FILES_DIR, *paths)
def get_usr(*paths):
    return os.path.join(LV_DIR, *paths)
def get_fw():
    return os.path.join(FIREWALL_DIR, "firewall.csv")
def get_logf(*paths):
    return os.path.join(LOG_DIR, *paths)


def export_firewall_settings(file):
    if " " in file and not file[0] == file[1] == '"':
        file = '"%s"'%file
    cmd = 'powershell -command "(New-Object -comObject HNetCfg.FWPolicy2).rules | export-csv %s -NoTypeInformation"'%file
    subprocess.call(cmd)


def lines(csv):
    with open(csv, 'r') as f:
        matrix = [[s.strip('"') for s in l.split(",")] for l in f.read().splitlines()]
    return sorted(matrix)

def firewall_compare(ref, tmpfile):
    rlines = lines(ref)
    tlines = lines(tmpfile)
    return rlines == tlines


def compare_firewall_settings():
    with tempfile.TemporaryDirectory() as p:
        ref = get_fw()
        tmp = os.path.join(p, "fw_settings.csv")
        export_firewall_settings(tmp)
        eq = firewall_compare(ref, tmp)
    if eq:
        print("Firewall match success")
    else:
        print("Firewall match failure")


def compare_config_files():
    files = [
        ("sysvars", "System Variables.sys"),
        ("alarms", "Alarms Off.alm"),
        ("alarms", "Alarms On.alm"),
        ("loggersettings", "Logging Off.log"),
        ("loggersettings", "Logging On.log"),
        ("emailsettings", "Email Alerts Settings.xml"),
    ]
    for typ, fn in files:
        ref = get_ref(fn)
        usr = get_usr(fn)
        lf  = get_logf(fn+" Report.txt")
        n, report = file_compare(typ, ref, usr, outfmt="txt", always_show_names=False)
        if n:
            print("\t%d Setting(s) mismatch:"%n)
            print(report)
        else:
            print("\t%s: Match"%fn)
        with open(lf, 'w') as f:
            f.write(report)


if __name__ == "__main__":
    print("Comparing firewall settings...")
    compare_firewall_settings()
    print("Comparing config files...")
    compare_config_files()

