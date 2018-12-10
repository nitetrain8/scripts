"""

Created by: Nathan Starkweather
Created on: 02/20/2016
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import logging

logger = logging.getLogger(__name__)

from goffice2 import *
path = "C:\\Users\\Administrator\\Documents\\python\\db_stuff\\data\\.auth\\_exp_auth_key.json"
creds = load_credentials(path)


def dump_most_attrs(ob):

    for attr in dir(ob):
        if attr.startswith("_"):
            continue
        try:
            val = getattr(ob, attr)
        except Exception:
            print("Error getting attribute: %s" % attr)
            continue
        if callable(val):
            continue
        print("%s: %s" % (attr, val))

import sqlite3
sqlite3.Statement
